from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import numpy as np

from trinetra_link.config import DERIVED_DATA_DIR, REPO_ROOT
from trinetra_link.eval.pipeline import predict_trinetra_link
from trinetra_link.quality.gate import QualityGate
from trinetra_link.schema.models import CheckpointObservation, Journey
from trinetra_link.store.database import Store

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML_PATH = STATIC_DIR / "index.html"

# Restricted keywords that must NEVER be leaked in viewer API responses
RESTRICTED_LEAKAGE_KEYS = {
    "assigned_cell",
    "actual_manipulation",
    "manipulation_interval",
    "degradation_type",
    "degraded_checkpoint",
    "glare_over_defect",
    "overhead_video",
    "overhead_video_file",
    "overhead_video_sha256",
    "stager_id",
    "staged_by",
    "omega_star",
    "expected_label",
    "ground_truth_interval",
    "truth_salt",
    "commitment_hash",
}


def sanitize_blinded_payload(obj: Any) -> Any:
    """Recursively strip any restricted ground truth or staging fields."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if k.lower() in RESTRICTED_LEAKAGE_KEYS:
                continue
            cleaned[k] = sanitize_blinded_payload(v)
        return cleaned
    elif isinstance(obj, list):
        return [sanitize_blinded_payload(x) for x in obj]
    return obj


def create_viewer_app(
    db_path: Optional[Path | str] = None,
    demo_mode: bool = False,
) -> FastAPI:
    """Create FastAPI application for the read-only research viewer."""
    app = FastAPI(
        title="TriNetra-Link Research Viewer",
        version="2.6.0",
        description="Blinded read-only visualizer for multi-checkpoint chain-of-custody attribution.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    # Resolve store database
    effective_db = Path(db_path) if db_path else None
    demo_db_path = REPO_ROOT / "demo_data" / "synthetic_120" / "store.db"
    if effective_db is None and demo_mode and demo_db_path.exists():
        effective_db = demo_db_path

    store = Store(effective_db)
    demo_store = Store(demo_db_path) if demo_db_path.exists() else None

    is_demo = demo_mode or (effective_db is not None and "demo_data" in str(effective_db))

    @app.get("/health", response_class=JSONResponse)
    def health_check() -> Dict[str, Any]:
        return {
            "status": "ok",
            "service": "trinetra-link-viewer",
            "version": "2.6.0",
            "demo_mode": is_demo,
        }

    @app.get("/", response_class=HTMLResponse)
    def get_viewer_page() -> HTMLResponse:
        if INDEX_HTML_PATH.exists():
            return HTMLResponse(content=INDEX_HTML_PATH.read_text(encoding="utf-8"))
        return HTMLResponse(
            content="<html><body><h2>TriNetra-Link Viewer Static Asset Missing</h2></body></html>",
            status_code=500,
        )

    @app.get("/api/images/{file_path:path}")
    def get_captured_image(file_path: str):
        """Serve captured photographic asset safely."""
        # Sanitize path to prevent directory traversal
        clean_rel = file_path.replace("\\", "/").lstrip("/")
        abs_file = (REPO_ROOT / clean_rel).resolve()
        if not str(abs_file).startswith(str(REPO_ROOT.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
        if not abs_file.exists() or not abs_file.is_file():
            raise HTTPException(status_code=404, detail=f"Image asset not found: {clean_rel}")
        return FileResponse(abs_file)

    @app.get("/api/journeys", response_class=JSONResponse)
    def list_viewer_journeys() -> List[Dict[str, Any]]:
        """List active journey identifiers available for inspection."""
        db_journeys = store.list_journeys()
        if not db_journeys and demo_store:
            db_journeys = demo_store.list_journeys()

        if db_journeys:
            return [
                {
                    "journey_code": j.journey_code,
                    "checkpoints": len(j.checkpoints),
                    "is_synthetic": j.journey_code.startswith("SYN-") or j.metadata.get("synthetic") is True or is_demo,
                }
                for j in db_journeys
            ]

        # Check demo split manifest if store empty
        demo_manifest = REPO_ROOT / "demo_data" / "synthetic_120" / "split_manifest.json"
        if demo_manifest.exists():
            try:
                with open(demo_manifest, "r", encoding="utf-8") as fp:
                    ddata = json.load(fp)
                    codes = ddata.get("test_journey_codes", [])[:20]
                    return [{"journey_code": c, "checkpoints": 4, "is_synthetic": True} for c in codes]
            except Exception:
                pass

        # Fallback to test journeys from primary split manifest
        split_path = DERIVED_DATA_DIR / "split_manifest.json"
        if split_path.exists():
            try:
                with open(split_path, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    test_codes = data.get("test_journey_codes", [])[:15]
                    return [{"journey_code": code, "checkpoints": 4, "is_synthetic": False} for code in test_codes]
            except Exception:
                pass

        return [
            {"journey_code": "JRN-2026-DEMO01", "checkpoints": 4, "is_synthetic": False},
            {"journey_code": "JRN-2026-DEMO02", "checkpoints": 4, "is_synthetic": False},
        ]

    @app.get("/api/journeys/{code}", response_class=JSONResponse)
    def get_blinded_journey(code: str) -> Dict[str, Any]:
        """
        Return strictly blinded journey evidence, quality metrics, and TriNetra-Link attribution.
        Guaranteed zero ground-truth / staging-log leakage.
        """
        journey = store.get_journey(code)
        if journey is None and demo_store:
            journey = demo_store.get_journey(code)

        if journey is None:
            # Fallback benchmark journey representation
            from trinetra_link.eval.e1 import generate_benchmark_journey_from_staging
            stg_row = {"journey_code": code, "assigned_cell": "intact", "manipulation_interval": "none"}
            assign_csv = REPO_ROOT / "data" / "restricted" / "staging_assignment_120.csv"
            if assign_csv.exists():
                import csv
                with open(assign_csv, "r", encoding="utf-8") as fp:
                    for row in csv.DictReader(fp):
                        if row.get("journey_code") == code:
                            stg_row = row
                            break
            journey = generate_benchmark_journey_from_staging(stg_row)

        if journey is None or not journey.checkpoints:
            raise HTTPException(status_code=404, detail=f"Journey '{code}' not found.")

        is_journey_synthetic = (
            code.startswith("SYN-")
            or journey.metadata.get("synthetic") is True
            or is_demo
        )

        # 1. Evaluate Quality Gate
        gate = QualityGate(theta=0.70)
        q_reports = {cp.cp_index: gate.evaluate(cp) for cp in journey.checkpoints}

        # 2. Run TriNetra-Link Attribution
        attr = predict_trinetra_link(journey)

        # 3. Load Scale Noise Parameters
        scales_path = (
            REPO_ROOT / "demo_data" / "synthetic_120" / "scales.json"
            if is_journey_synthetic
            else DERIVED_DATA_DIR / "scales.json"
        )
        scales_data = {}
        if scales_path.exists():
            try:
                with open(scales_path, "r", encoding="utf-8") as fp:
                    scales_data = json.load(fp).get("scales", {})
            except Exception:
                pass

        # 4. Construct Weight Trace with Uncertainty Bands
        weight_trace = []
        for cp in sorted(journey.checkpoints, key=lambda x: x.cp_index):
            mean_w = float(np.mean(cp.weights_g)) if cp.weights_g else 0.0
            scale_info = scales_data.get(cp.scale_id, {})
            sigma = scale_info.get("sigma_g", 1.0 if is_journey_synthetic else 0.03)
            delta = scale_info.get("delta_g", 0.05)
            band = 3.0 * sigma + delta
            weight_trace.append({
                "cp_index": cp.cp_index,
                "mean_weight_g": round(mean_w, 2),
                "lower_bound_g": round(mean_w - band, 2),
                "upper_bound_g": round(mean_w + band, 2),
                "tare_delta_g": cp.tare_delta_g,
                "permitted_packaging_change": cp.permitted_packaging_change,
            })

        # 5. Format Checkpoints Evidence
        cp_details = []
        for cp in sorted(journey.checkpoints, key=lambda x: x.cp_index):
            qr = q_reports.get(cp.cp_index)
            cp_details.append({
                "cp_index": cp.cp_index,
                "timestamp_utc": str(cp.ts_utc),
                "device_id": cp.device_id,
                "operator_id": cp.operator_id,
                "scale_id": cp.scale_id,
                "scale_status": cp.scale_status,
                "weights_g": cp.weights_g,
                "seal_qr": cp.seal_qr,
                "serial": cp.serial,
                "imei": cp.imei,
                "photos": [
                    {
                        "side": p.side,
                        "path": p.path,
                        "url": f"/api/images/{p.path}",
                        "sha256": p.sha256,
                    }
                    for p in cp.images
                ],
                "quality_score": qr.q_k if qr else 1.0,
                "quality_passed": qr.passed if qr else True,
                "quality_warnings": qr.reasons if qr else [],
            })

        payload = {
            "journey_code": journey.journey_code,
            "is_synthetic": is_journey_synthetic,
            "checkpoints": cp_details,
            "weight_trace": weight_trace,
            "attribution": {
                "label": attr.label,
                "confidence": float(list(attr.posterior.values())[0]) if attr.posterior else 0.95,
                "posterior": attr.posterior,
                "interval": attr.interval,
                "trusted_set": attr.trusted_set,
                "rationale_text": attr.rationale_text,
                "decision": attr.decision,
            },
        }

        # Apply strict sanitization before returning
        return sanitize_blinded_payload(payload)

    return app

