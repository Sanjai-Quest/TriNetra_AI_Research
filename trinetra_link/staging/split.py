from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import random
from typing import Any, Dict, List, Optional

from trinetra_link.config import DERIVED_DATA_DIR, RESTRICTED_DATA_DIR
from trinetra_link.staging.assign import CELL_QUOTAS

DEFAULT_SPLIT_MANIFEST_PATH = DERIVED_DATA_DIR / "split_manifest.json"

# Stratified targets (sum: 24 calibration, 96 test)
CALIBRATION_QUOTAS = {
    "intact": 6,
    "permitted_flyer": 2,
    "forward_transit_damage": 3,
    "doorstep_substitution": 3,
    "customer_tamper": 3,
    "reverse_transit_tamper": 2,
    "degraded_evidence": 2,
    "ambiguous_evidence": 3,
}


def perform_stratified_split(
    assignments_csv_path: Optional[Path | str] = None,
    seed: int = 42,
    output_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """
    Partition N=120 physical journeys into a stratified 24-calibration / 96-test split.
    Records mapping in data/derived/split_manifest.json.
    """
    path = Path(assignments_csv_path) if assignments_csv_path else RESTRICTED_DATA_DIR / "staging_assignment_120.csv"
    if not path.exists():
        raise FileNotFoundError(f"Assignment sheet not found at {path}")

    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if len(rows) != 120:
        raise ValueError(f"Expected 120 assigned journeys, found {len(rows)}")

    # Group by cell
    by_cell: Dict[str, List[Dict[str, str]]] = {cell: [] for cell in CELL_QUOTAS}
    for r in rows:
        cell = r["assigned_cell"]
        if cell in by_cell:
            by_cell[cell].append(r)
        else:
            raise ValueError(f"Unknown cell '{cell}' in assignment row")

    rng = random.Random(seed)
    calibration_codes: List[str] = []
    test_codes: List[str] = []
    split_map: Dict[str, str] = {}

    for cell, items in by_cell.items():
        rng.shuffle(items)
        n_cal = CALIBRATION_QUOTAS[cell]
        cal_items = items[:n_cal]
        test_items = items[n_cal:]

        for it in cal_items:
            code = it["journey_code"]
            calibration_codes.append(code)
            split_map[code] = "calibration"

        for it in test_items:
            code = it["journey_code"]
            test_codes.append(code)
            split_map[code] = "test"

    assert len(calibration_codes) == 24, f"Calibration count {len(calibration_codes)} != 24"
    assert len(test_codes) == 96, f"Test count {len(test_codes)} != 96"

    manifest = {
        "version": "2.6.0",
        "seed": seed,
        "split_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_journeys": 120,
        "calibration_count": len(calibration_codes),
        "test_count": len(test_codes),
        "calibration_by_cell": CALIBRATION_QUOTAS,
        "calibration_journey_codes": sorted(calibration_codes),
        "test_journey_codes": sorted(test_codes),
        "split_mapping": split_map,
    }

    out_file = Path(output_path) if output_path else DEFAULT_SPLIT_MANIFEST_PATH
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    return {
        "manifest_path": str(out_file),
        "calibration_count": len(calibration_codes),
        "test_count": len(test_codes),
    }
