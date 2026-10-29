from __future__ import annotations

import csv
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import random
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from trinetra_link.config import REPO_ROOT
from trinetra_link.schema.models import CheckpointObservation, ImageRef, Journey
from trinetra_link.staging.assign import CELL_QUOTAS
from trinetra_link.staging.determinability import derive_ground_truth, get_determinability_rule_hash
from trinetra_link.staging.split import CALIBRATION_QUOTAS
from trinetra_link.store.database import Store

DEFAULT_SYNTHETIC_DIR = REPO_ROOT / "demo_data" / "synthetic_120"

# Realistic high-value parcel item catalogue
SYNTHETIC_ITEMS = [
    {"name": "Smartphone Pro Max", "base_mass_g": 220.0, "category": "ELECTRONICS"},
    {"name": "ANC Wireless Headphones", "base_mass_g": 250.0, "category": "AUDIO"},
    {"name": "GPS Smartwatch Titanium", "base_mass_g": 62.0, "category": "WEARABLES"},
    {"name": "Mechanical Keyboard 75%", "base_mass_g": 810.0, "category": "PERIPHERALS"},
    {"name": "Ultra-thin 10-inch Tablet", "base_mass_g": 475.0, "category": "TABLETS"},
    {"name": "External NVMe SSD 1TB", "base_mass_g": 85.0, "category": "STORAGE"},
]


def render_synthetic_box_image(
    side: str,
    journey_code: str,
    cp_index: int,
    seal_qr: str,
    output_path: Path | str,
    is_damaged: bool = False,
    is_tampered_seal: bool = False,
    is_degraded_dark: bool = False,
    has_glare: bool = False,
    serial_no: str = "SN-SYN-10293",
) -> str:
    """
    Render 640x480 synthetic parcel box photograph.
    Stamps 'SYNTHETIC DEMO' banner on every image.
    Returns SHA-256 hex digest of the saved JPEG.
    """
    w, h = 640, 480
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    # 1. Base Dark Degradation Mode
    if is_degraded_dark:
        # Near-black underexposed frame
        img = Image.new("RGB", (w, h), color=(14, 14, 16))
        draw = ImageDraw.Draw(img)
        # Add faint sensor noise
        for y in range(0, h, 8):
            draw.line([(0, y), (w, y)], fill=(18, 18, 22), width=1)
        # Stamp watermark
        draw.rectangle([10, 10, 195, 38], fill=(180, 20, 20))
        draw.text((18, 16), "SYNTHETIC DEMO", fill=(255, 255, 255))
        draw.text((18, 450), f"[DARK DEGRADED] {journey_code} CP{cp_index}", fill=(100, 100, 110))
        img.save(out_p, format="JPEG", quality=75)
        return hashlib.sha256(out_p.read_bytes()).hexdigest()

    # 2. Standard Background (Warehouse inspection bench)
    img = Image.new("RGB", (w, h), color=(222, 224, 228))
    draw = ImageDraw.Draw(img)

    # Grid lines on tabletop
    for x in range(0, w, 40):
        draw.line([(x, 0), (x, h)], fill=(210, 212, 216), width=1)
    for y in range(0, h, 40):
        draw.line([(0, y), (w, y)], fill=(210, 212, 216), width=1)

    if side == "TOP":
        # Cardboard Carton Box Top
        draw.rectangle([110, 75, 530, 405], fill=(206, 178, 138), outline=(155, 126, 88), width=3)
        # Carton center seam
        draw.line([(320, 75), (320, 405)], fill=(160, 130, 90), width=2)
        # Packaging tape along seam
        draw.rectangle([310, 75, 330, 405], fill=(232, 222, 200), outline=(210, 200, 180))

        # Tamper-evident Security Tape across the seam
        draw.rectangle([210, 215, 430, 265], fill=(0, 140, 210), outline=(0, 110, 175), width=2)
        draw.text((220, 230), f"SEAL: {seal_qr[:16]}", fill=(255, 255, 255))

        # Carton Damage / Rupture
        if is_damaged:
            dent_poly = [(110, 75), (170, 75), (145, 125), (110, 145)]
            draw.polygon(dent_poly, fill=(130, 100, 65), outline=(90, 65, 40))
            draw.line([(110, 145), (180, 105)], fill=(70, 50, 30), width=2)
            draw.line([(145, 125), (195, 140)], fill=(70, 50, 30), width=2)
            draw.text((120, 155), "[CARTON DENT]", fill=(120, 30, 30))

        # Tampered / Cut Seal
        if is_tampered_seal:
            cut_pts = [(210, 240), (270, 230), (320, 248), (370, 232), (430, 242)]
            draw.line(cut_pts, fill=(230, 20, 20), width=4)
            draw.text((250, 270), ">>> TAMPER VOID / RESEALED <<<", fill=(210, 20, 20))

    elif side == "LABEL":
        # Carton front/side with shipping label
        draw.rectangle([100, 80, 540, 400], fill=(195, 168, 128), outline=(150, 120, 80), width=3)
        # White address label
        draw.rectangle([150, 120, 490, 360], fill=(255, 255, 255), outline=(180, 180, 180), width=2)
        # Header banner
        draw.rectangle([150, 120, 490, 160], fill=(40, 60, 90))
        draw.text((170, 132), "EXPRESS LOGISTICS • PRIORITY AIR", fill=(255, 255, 255))

        # Shipping details
        draw.text((170, 175), f"JOURNEY:  {journey_code}", fill=(20, 20, 20))
        draw.text((170, 195), f"SERIAL:   {serial_no}", fill=(20, 20, 20))
        draw.text((170, 215), f"ORIGIN:   DELHI HUB-01", fill=(60, 60, 60))
        draw.text((170, 235), f"DEST:     BOM GATEWAY-04", fill=(60, 60, 60))

        # Barcode stripes
        bx = 170
        for w_bar in [3, 1, 4, 2, 5, 2, 3, 1, 4, 2, 3, 5, 2, 4, 1, 3, 2, 5, 3]:
            draw.rectangle([bx, 265, bx + w_bar, 320], fill=(0, 0, 0))
            bx += w_bar + 4
        draw.text((170, 330), "*99281729019283*", fill=(50, 50, 50))

    else:  # "SEAL"
        # Close-up macro view of security seal
        draw.rectangle([80, 120, 560, 360], fill=(200, 170, 130), outline=(150, 120, 80), width=2)
        draw.rectangle([120, 180, 520, 290], fill=(0, 140, 210), outline=(0, 100, 160), width=3)
        draw.text((140, 200), f"SECURITY SEAL ID: {seal_qr}", fill=(255, 255, 255))
        draw.text((140, 225), "DO NOT ACCEPT IF SEAL IS BROKEN OR VOID EXPOSED", fill=(220, 240, 255))

        if is_tampered_seal:
            # Broken seal fibers & red fracture line
            draw.line([(120, 235), (280, 220), (340, 250), (420, 225), (520, 240)], fill=(240, 20, 20), width=5)
            draw.text((200, 305), "TAMPER INDICATOR: VOID OPEN EXPOSED", fill=(220, 20, 20))
        else:
            draw.text((140, 250), "STATUS: INTACT & VERIFIED", fill=(200, 255, 200))

    # 3. Bright Glare Blob for AMBIGUOUS cells
    if has_glare:
        # Concentric bright white/yellow glare ellipses over center/seal
        glare_centers = [(320, 240), (330, 235), (315, 245)]
        for gx, gy in glare_centers:
            draw.ellipse([gx - 90, gy - 65, gx + 90, gy + 65], fill=(255, 255, 230), outline=(255, 250, 200))
            draw.ellipse([gx - 60, gy - 45, gx + 60, gy + 45], fill=(255, 255, 255))
        draw.text((230, 320), "⚠️ OPTICAL GLARE REFLECTION OVER SEAL", fill=(180, 50, 20))

    # 4. Mandatory Corner Watermarks
    # Top-Left Red Banner
    draw.rectangle([10, 10, 195, 38], fill=(220, 30, 30), outline=(160, 20, 20), width=1)
    draw.text((18, 16), "SYNTHETIC DEMO", fill=(255, 255, 255))

    # Bottom-Right Metadata Stamp
    draw.text((360, 452), f"SYNTHETIC • {journey_code} CP{cp_index} {side}", fill=(100, 105, 115))

    img.save(out_p, format="JPEG", quality=82)
    return hashlib.sha256(out_p.read_bytes()).hexdigest()


def generate_synthetic_dryrun_dataset(
    output_dir: Optional[Path | str] = None,
    scale_sigma: float = 1.0,
    seed: int = 777,
) -> Dict[str, Any]:
    """
    Generate synthetic dry-run study dataset of exactly N=120 journeys across the 8 scenario cells:
      - 30 intact
      - 12 permitted_flyer
      - 14 forward_transit_damage
      - 14 doorstep_substitution
      - 14 customer_tamper
      - 12 reverse_transit_tamper
      - 12 degraded_evidence
      - 12 ambiguous_evidence
    Total: 120 journeys, 480 checkpoints.
    Partitioned into stratified 24 calibration / 96 test split.
    All journey codes carry 'SYN-2026-XXXX'.
    All records carry 'synthetic': True.
    Writes strictly to demo_data/synthetic_120/.
    """
    target_dir = (Path(output_dir).resolve() if output_dir else DEFAULT_SYNTHETIC_DIR).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    images_dir = target_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    # 1. Pool assignment cells
    pool: List[Dict[str, str]] = []
    for cell_id, info in CELL_QUOTAS.items():
        for _ in range(info["count"]):
            pool.append({
                "assigned_cell": cell_id,
                "target_interval": info["target_interval"],
                "description": info["description"],
            })

    rng.shuffle(pool)
    assert len(pool) == 120, f"Expected 120 pooled cells, got {len(pool)}"

    # 2. Assign unique synthetic journey codes: SYN-2026-0001 .. SYN-2026-0120
    assignment_rows: List[Dict[str, Any]] = []
    for idx, item in enumerate(pool, start=1):
        assignment_rows.append({
            "order_index": idx,
            "journey_code": f"SYN-2026-{idx:04d}",
            "assigned_cell": item["assigned_cell"],
            "target_interval": item["target_interval"],
            "cell_description": item["description"],
            "synthetic": True,
        })

    # 3. Create Stratified Split (24 Calibration / 96 Test)
    by_cell: Dict[str, List[Dict[str, Any]]] = {cell: [] for cell in CELL_QUOTAS}
    for r in assignment_rows:
        by_cell[r["assigned_cell"]].append(r)

    cal_codes: List[str] = []
    test_codes: List[str] = []
    split_map: Dict[str, str] = {}

    for cell, rows in by_cell.items():
        rng.shuffle(rows)
        n_cal = CALIBRATION_QUOTAS[cell]
        for r in rows[:n_cal]:
            cal_codes.append(r["journey_code"])
            split_map[r["journey_code"]] = "calibration"
        for r in rows[n_cal:]:
            test_codes.append(r["journey_code"])
            split_map[r["journey_code"]] = "test"

    assert len(cal_codes) == 24
    assert len(test_codes) == 96

    # 4. Generate Telemetry, Images & Journey Objects
    db_path = target_dir / "store.db"
    if db_path.exists():
        db_path.unlink()
    store = Store(db_path)

    staging_log_rows: List[Dict[str, Any]] = []
    ground_truth_records: List[Dict[str, Any]] = []
    journeys: List[Journey] = []

    base_time = datetime(2026, 10, 1, 8, 0, 0, tzinfo=timezone.utc)

    for r in assignment_rows:
        code = r["journey_code"]
        cell = r["assigned_cell"]
        interval = r["target_interval"]

        # Item and baseline mass
        item_spec = rng.choice(SYNTHETIC_ITEMS)
        nominal_packaging_tare = 75.0
        w_baseline = item_spec["base_mass_g"] + nominal_packaging_tare

        # Cell manipulation parameters
        tamper_stage = 0
        if interval.startswith("S") and len(interval) >= 2:
            try:
                tamper_stage = int(interval[1])
            except ValueError:
                pass

        # Degradation & Glare parameters
        degraded_cp = "none"
        degradation_type = "none"
        has_glare = False

        if cell == "degraded_evidence":
            # Bounding checkpoint degraded: alternate between CP2 and CP3
            degraded_cp = "cp2" if (int(code[-4:]) % 2 == 0) else "cp3"
            degradation_type = "scale_error"
        elif cell == "ambiguous_evidence":
            has_glare = True

        stg_row = {
            "journey_code": code,
            "assigned_cell": cell,
            "manipulation_interval": interval,
            "actual_manipulation": "none" if interval == "none" else f"tamper_{cell}",
            "tare_adjusted": "yes" if cell == "permitted_flyer" else "no",
            "degraded_checkpoint": degraded_cp,
            "degradation_type": degradation_type,
            "glare_over_defect": "yes" if has_glare else "no",
            "overhead_video_sha256": hashlib.sha256(f"OVERHEAD_SYN_{code}".encode()).hexdigest(),
            "staged_by": "SYNTHETIC_DEMO_GENERATOR",
            "synthetic": "true",
        }
        staging_log_rows.append(stg_row)

        # Derive Ground Truth (Amendment v2.6 §4.3)
        omega_star, expected_label, gt_interval = derive_ground_truth(stg_row)
        ground_truth_records.append({
            "journey_code": code,
            "assigned_cell": cell,
            "omega_star": omega_star,
            "expected_label": expected_label,
            "ground_truth_interval": gt_interval,
            "synthetic": True,
        })

        # Generate Checkpoints CP1..CP4
        w_curr = w_baseline
        tare_delta = 15.0 if cell == "permitted_flyer" else 0.0
        cps: List[CheckpointObservation] = []
        serial_no = f"SN-SYN-{code[-4:]}982"
        imei_no = f"35987102983{code[-4:]}"
        orig_seal = f"SEAL-SYN-{code[-4:]}"

        for k in (1, 2, 3, 4):
            cp_time = base_time + timedelta(hours=(k - 1) * 3)

            # Permitted packaging change at CP2
            is_permitted = (cell == "permitted_flyer" and k == 2)
            if is_permitted:
                w_curr += tare_delta

            # Manipulation step
            if tamper_stage > 0 and k > tamper_stage:
                if cell == "forward_transit_damage":
                    w_curr -= 5.0  # Weight loss from carton rupture
                elif cell in ("doorstep_substitution", "customer_tamper", "reverse_transit_tamper", "degraded_evidence"):
                    w_curr -= 42.0  # Item substituted with lighter surrogate
                elif cell == "ambiguous_evidence":
                    pass  # Defect obscured by glare; no weight change

            # Checkpoint degradation flags
            is_cp_degraded = (degraded_cp == f"cp{k}")
            is_cp_glare = (has_glare and k >= 3)
            is_tampered_state = (tamper_stage > 0 and k > tamper_stage)

            # Weights
            if is_cp_degraded:
                scale_status = "ERROR"
                readings = []  # No weights at degraded checkpoint
            else:
                scale_status = "OK"
                noise = np_rng.normal(0.0, scale_sigma, size=3)
                readings = [round(float(w_curr + n), 2) for n in noise]

            # Seal identifier
            if is_tampered_state and cell in ("doorstep_substitution", "customer_tamper", "reverse_transit_tamper", "degraded_evidence"):
                seal_qr = f"SEAL-VOID-{code[-4:]}"
            else:
                seal_qr = orig_seal

            carrier_notes = "Camera glare over defect" if is_cp_glare else ""

            # Render Photos (TOP, LABEL, SEAL)
            cp_images: List[ImageRef] = []
            for side in ("TOP", "LABEL", "SEAL"):
                img_filename = f"{code}_CP{k}_{side}.jpg"
                img_path = images_dir / img_filename

                img_sha = render_synthetic_box_image(
                    side=side,
                    journey_code=code,
                    cp_index=k,
                    seal_qr=seal_qr,
                    output_path=img_path,
                    is_damaged=(cell == "forward_transit_damage" and is_tampered_state),
                    is_tampered_seal=(is_tampered_state and cell != "forward_transit_damage"),
                    is_degraded_dark=is_cp_degraded,
                    has_glare=is_cp_glare,
                    serial_no=serial_no,
                )

                # Store relative path from repository root
                rel_img_path = str(img_path.relative_to(REPO_ROOT)).replace("\\", "/")
                cp_images.append(ImageRef(
                    side=side,
                    path=rel_img_path,
                    sha256=img_sha,
                    w=640,
                    h=480,
                ))

            cp_obs = CheckpointObservation(
                journey_code=code,
                cp_index=k,
                ts_utc=cp_time,
                device_id=f"DEV_SYN_CP{k}",
                operator_id=f"OP_SYN_0{k}",
                weights_g=readings,
                scale_id="SCALE_SYN_01",
                scale_status=scale_status,
                seal_qr=seal_qr,
                serial=serial_no,
                imei=imei_no,
                carrier_log=carrier_notes,
                permitted_packaging_change=is_permitted,
                tare_delta_g=tare_delta if is_permitted else 0.0,
                images=cp_images,
            )
            cps.append(cp_obs)

        journey = Journey(
            journey_code=code,
            checkpoints=cps,
            metadata={
                "synthetic": True,
                "demo_fixture": True,
                "assigned_cell": cell,
                "target_interval": interval,
                "nominal_weight_g": round(w_baseline, 2),
                "item_name": item_spec["name"],
                "split": split_map[code],
            },
        )
        journeys.append(journey)

        # Store in SQLite database
        store.insert_journey(journey)
        for cp in cps:
            store.insert_checkpoint(cp)

    # 5. Save Files
    # (A) Assignment CSV
    assign_csv = target_dir / "staging_assignment_120.csv"
    with open(assign_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["order_index", "journey_code", "assigned_cell", "target_interval", "cell_description", "synthetic"]
        )
        writer.writeheader()
        writer.writerows(assignment_rows)

    # (B) Assignment JSON
    assign_json = target_dir / "staging_assignment_120.json"
    with open(assign_json, "w", encoding="utf-8") as f:
        json.dump({
            "version": "2.6.0-synthetic",
            "synthetic": True,
            "disclaimer": "SYNTHETIC DEMO ONLY — DO NOT REPORT AS EMPIRICAL RESULTS",
            "n": 120,
            "seed": seed,
            "cell_counts": {k: v["count"] for k, v in CELL_QUOTAS.items()},
            "assignments": assignment_rows,
        }, f, indent=2)

    # (C) Staging Log CSV
    staging_log_csv = target_dir / "staging_log_120.csv"
    fieldnames = [
        "journey_code", "assigned_cell", "manipulation_interval", "actual_manipulation",
        "tare_adjusted", "degraded_checkpoint", "degradation_type", "glare_over_defect",
        "overhead_video_sha256", "staged_by", "synthetic"
    ]
    with open(staging_log_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(staging_log_rows)

    # (D) Split Manifest JSON
    split_manifest_json = target_dir / "split_manifest.json"
    with open(split_manifest_json, "w", encoding="utf-8") as f:
        json.dump({
            "version": "2.6.0-synthetic",
            "synthetic": True,
            "disclaimer": "SYNTHETIC DRY RUN — NOT A RESULT",
            "total_journeys": 120,
            "calibration_count": 24,
            "test_count": 96,
            "calibration_journey_codes": sorted(cal_codes),
            "test_journey_codes": sorted(test_codes),
            "split_mapping": split_map,
        }, f, indent=2)

    # (E) Scales Config JSON
    scales_json = target_dir / "scales.json"
    with open(scales_json, "w", encoding="utf-8") as f:
        json.dump({
            "version": "2.6.0-synthetic",
            "synthetic": True,
            "disclaimer": "SYNTHETIC DRY RUN SCALE NOISE MODEL",
            "scales": {
                "SCALE_SYN_01": {
                    "scale_id": "SCALE_SYN_01",
                    "sigma_g": scale_sigma,
                    "delta_g": 0.05,
                }
            }
        }, f, indent=2)

    # (F) Ground Truth JSON
    gt_json = target_dir / "ground_truth_120.json"
    gt_counts = {"OBS_DETERMINABLE": 0, "OBS_DEGRADED_INCOMPLETE": 0, "OBS_INDISTINGUISHABLE": 0}
    for gtr in ground_truth_records:
        gt_counts[gtr["omega_star"]] = gt_counts.get(gtr["omega_star"], 0) + 1

    with open(gt_json, "w", encoding="utf-8") as f:
        json.dump({
            "version": "2.6.0-synthetic",
            "synthetic": True,
            "disclaimer": "SYNTHETIC DEMO GROUND TRUTH",
            "rule_sha256": get_determinability_rule_hash(),
            "total_journeys": len(ground_truth_records),
            "distribution": gt_counts,
            "records": ground_truth_records,
        }, f, indent=2)

    return {
        "status": "success",
        "synthetic": True,
        "n_journeys": len(journeys),
        "calibration_count": len(cal_codes),
        "test_count": len(test_codes),
        "scale_sigma": scale_sigma,
        "seed": seed,
        "output_dir": str(target_dir),
        "db_path": str(db_path),
        "split_manifest": str(split_manifest_json),
        "staging_log": str(staging_log_csv),
        "assignment_csv": str(assign_csv),
        "scales_json": str(scales_json),
        "ground_truth_json": str(gt_json),
        "total_images": len(journeys) * 4 * 3,
    }


if __name__ == "__main__":
    import sys
    print("Generating synthetic dry-run study dataset (120 journeys)...")
    res = generate_synthetic_dryrun_dataset()
    print(f"Generated {res['n_journeys']} synthetic journeys -> {res['output_dir']}")
    print(f"Images rendered: {res['total_images']}")
