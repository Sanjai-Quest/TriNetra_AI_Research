from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Path as FPath, Query, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image
import io

from trinetra_link import __version__
from trinetra_link.config import ARTIFACTS_DIR, REPO_ROOT
from trinetra_link.quality.gate import QualityGate
from trinetra_link.reconcile.fuse import fuse_checkpoint_observations
from trinetra_link.schema.models import CheckpointObservation, ImageRef, Journey, QualityReport
from trinetra_link.store.database import Store

STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_STORAGE_DIR = ARTIFACTS_DIR / "images"
IMAGES_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Device authentication token
DEFAULT_DEV_TOKEN = "trinetra-dev-capture-token"


def get_expected_token() -> str:
    return os.getenv("DEVICE_INGEST_TOKEN", DEFAULT_DEV_TOKEN)


def verify_device_token(
    x_device_token: Optional[str] = Header(None, alias="X-Device-Token"),
    token: Optional[str] = Query(None),
) -> str:
    expected = get_expected_token()
    provided = x_device_token or token
    if not provided or provided != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Missing or invalid device capture token",
        )
    return provided


app = FastAPI(
    title="TriNetra-Link Ingest API",
    description="Multimodal Physical Observation Ingest & Evidence Capture Service",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared store instance (configurable via env)
def get_store() -> Store:
    db_path = os.getenv("TRINETRA_DB_PATH")
    return Store(db_path)


class JourneyCreateRequest(BaseModel):
    journey_code: str
    metadata: Optional[Dict[str, Any]] = None


@app.get("/health", tags=["System"])
def health_check() -> Dict[str, str]:
    """Service health probe."""
    return {"status": "ok", "version": __version__}


@app.get("/", tags=["UI"])
def serve_capture_ui() -> FileResponse:
    """Serve the mobile-optimized capture client."""
    capture_html = STATIC_DIR / "capture.html"
    if not capture_html.exists():
        raise HTTPException(status_code=404, detail="capture.html UI not yet compiled")
    return FileResponse(str(capture_html))


@app.post("/journeys", status_code=status.HTTP_201_CREATED, tags=["Journeys"])
def create_journey(
    payload: JourneyCreateRequest,
    response: Response,
    store: Store = Depends(get_store),
    _token: str = Depends(verify_device_token),
) -> Dict[str, Any]:
    """Register a new physical journey container idempotently."""
    code = payload.journey_code.strip()
    if not code:
        raise HTTPException(status_code=400, detail="journey_code cannot be empty")

    existing = store.get_journey(code)
    if existing:
        response.status_code = status.HTTP_200_OK
        return {
            "status": "exists",
            "message": f"Journey {code} already registered",
            "journey": existing.model_dump(mode="json"),
        }

    journey = Journey(
        journey_code=code,
        status="ACTIVE",
        metadata=payload.metadata or {},
    )
    store.insert_journey(journey)
    return {
        "status": "created",
        "journey": journey.model_dump(mode="json"),
    }


@app.post("/journeys/{code}/checkpoints/{k}", status_code=status.HTTP_201_CREATED, tags=["Checkpoints"])
async def ingest_checkpoint(
    code: str = FPath(..., description="Journey code"),
    k: int = FPath(..., ge=1, le=10, description="Checkpoint sequence index (1..K)"),
    data: str = Form(..., description="JSON string of CheckpointObservation metadata"),
    files: List[UploadFile] = File(..., description="Photographic evidence assets"),
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    store: Store = Depends(get_store),
    _token: str = Depends(verify_device_token),
) -> Dict[str, Any]:
    """
    Ingest multipart checkpoint observation:
        - Validates checkpoint sequence order
        - Computes and verifies server-side SHA-256 for all images
        - Evaluates quality gate (q_k)
        - Executes multimodal baseline reconciliation against CP1 (for k > 1)
        - Persists append-only records to store
    """
    code = code.strip()
    journey = store.get_journey(code)
    if not journey:
        # Auto-create active journey container if not explicitly pre-registered
        journey = Journey(journey_code=code, status="ACTIVE")
        store.insert_journey(journey)

    # Sequence continuity check
    existing_cps = {cp.cp_index: cp for cp in store.list_checkpoints(code)}
    if k in existing_cps:
        raise HTTPException(status_code=400, detail=f"Checkpoint CP{k} has already been recorded for {code} (append-only)")
    if k > 1 and (k - 1) not in existing_cps:
        raise HTTPException(
            status_code=400,
            detail=f"Sequence violation: CP{k - 1} must be recorded before CP{k}",
        )

    # Parse metadata JSON
    try:
        meta_dict = json.loads(data)
    except json.JSONDecodeError as err:
        raise HTTPException(status_code=400, detail=f"Malformed metadata JSON in 'data' form field: {err}")

    # Process and verify image files
    if not files:
        raise HTTPException(status_code=400, detail="At least one photographic evidence file is required")

    client_hashes = meta_dict.get("client_hashes", {})
    image_refs: List[ImageRef] = []
    image_arrays: Dict[str, np.ndarray] = {}

    target_dir = IMAGES_STORAGE_DIR / code
    target_dir.mkdir(parents=True, exist_ok=True)

    for idx, upload in enumerate(files):
        contents = await upload.read()
        if not contents:
            raise HTTPException(status_code=400, detail=f"Uploaded file '{upload.filename}' is empty")

        server_sha256 = hashlib.sha256(contents).hexdigest()

        # Side name resolution (front, top, seal, back, etc.)
        filename = upload.filename or f"image_{idx}.jpg"
        side_candidate = filename.split(".")[0].split("_")[-1].lower()
        allowed_sides = ["front", "top", "seal", "back", "left", "right"]
        side = side_candidate if side_candidate in allowed_sides else (meta_dict.get("side") or f"side_{idx}")

        # Check client provided hash if present
        expected_client_hash = client_hashes.get(upload.filename) or client_hashes.get(side)
        if expected_client_hash and expected_client_hash.lower() != server_sha256.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Hash mismatch for '{upload.filename}': client={expected_client_hash}, server={server_sha256}",
            )

        # Decode image to inspect dimensions
        try:
            pil_img = Image.open(io.BytesIO(contents))
            w, h = pil_img.size
            # Convert to BGR array for CV quality checks
            cv_arr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            image_arrays[side] = cv_arr
        except Exception:
            w, h = 640, 480

        # Save to storage path
        storage_filename = f"cp{k}_{side}_{server_sha256[:8]}.jpg"
        storage_path = target_dir / storage_filename
        with open(storage_path, "wb") as f:
            f.write(contents)

        image_refs.append(
            ImageRef(
                side=side,
                path=str(storage_path),
                sha256=server_sha256,
                w=w,
                h=h,
                exposure=meta_dict.get("exposure"),
            )
        )

    # Build CheckpointObservation
    weights_g = meta_dict.get("weights_g", [])
    if not isinstance(weights_g, list) or len(weights_g) < 1:
        raise HTTPException(status_code=400, detail="weights_g must be a list with at least 1 reading (recommended >= 3)")

    ts_str = meta_dict.get("ts_utc")
    ts_utc = datetime.fromisoformat(ts_str.replace("Z", "+00:00")) if ts_str else datetime.now(timezone.utc)

    obs = CheckpointObservation(
        journey_code=code,
        cp_index=k,
        ts_utc=ts_utc,
        device_id=meta_dict.get("device_id", "MOBILE-CAPTURE-01"),
        operator_id=meta_dict.get("operator_id", "OPERATOR-DEFAULT"),
        weights_g=[float(w) for w in weights_g],
        scale_id=meta_dict.get("scale_id", "SCALE-MANUAL"),
        scale_status=meta_dict.get("scale_status", "OK"),
        calibration_date=meta_dict.get("calibration_date"),
        images=image_refs,
        seal_qr=meta_dict.get("seal_qr"),
        serial=meta_dict.get("serial"),
        imei=meta_dict.get("imei"),
        carrier_log=meta_dict.get("carrier_log"),
        permitted_packaging_change=bool(meta_dict.get("permitted_packaging_change", False)),
        tare_delta_g=float(meta_dict.get("tare_delta_g", 0.0)),
        app_version=meta_dict.get("app_version", __version__),
    )

    # Persist checkpoint to store
    store.insert_checkpoint(obs)

    # Quality Gate Evaluation
    prev_obs = existing_cps.get(k - 1)
    gate = QualityGate()
    quality_report = gate.evaluate(
        observation=obs,
        previous_observation=prev_obs,
        image_arrays=image_arrays,
    )
    store.insert_quality_report(quality_report)

    # Multimodal reconciliation vs CP1 (if k > 1)
    reconcile_res = None
    if k > 1 and 1 in existing_cps:
        cp1 = existing_cps[1]
        reconcile_res = fuse_checkpoint_observations(
            obs_baseline=cp1,
            obs_current=obs,
            quality_report=quality_report,
            image_arrays_current=image_arrays,
        )
        store.insert_reconcile_result(reconcile_res)

    return {
        "status": "success",
        "journey_code": code,
        "cp_index": k,
        "checkpoint": obs.model_dump(mode="json"),
        "quality_report": quality_report.model_dump(mode="json"),
        "reconcile_result": reconcile_res.model_dump(mode="json") if reconcile_res else None,
    }


@app.get("/journeys/{code}", tags=["Journeys"])
def get_journey_timeline(
    code: str = FPath(..., description="Journey code"),
    store: Store = Depends(get_store),
    _token: str = Depends(verify_device_token),
) -> Dict[str, Any]:
    """Retrieve full physical observation timeline for a journey."""
    journey = store.get_journey(code.strip())
    if not journey:
        raise HTTPException(status_code=404, detail=f"Journey '{code}' not found")

    return {
        "journey": journey.model_dump(mode="json"),
        "checkpoints_count": len(journey.checkpoints),
    }
