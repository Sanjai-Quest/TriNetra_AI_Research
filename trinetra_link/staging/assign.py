from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import random
from typing import Any, Dict, List, Optional

from trinetra_link.config import RESTRICTED_DATA_DIR

# The 8 canonical scenario cells from Amendment v2.6 §5
CELL_QUOTAS = {
    "intact": {"target_interval": "none", "count": 30, "description": "Intact legitimate transit"},
    "permitted_flyer": {"target_interval": "none", "count": 12, "description": "Permitted flyer-bag tare change"},
    "forward_transit_damage": {"target_interval": "S1", "count": 14, "description": "Forward transit carton impact"},
    "doorstep_substitution": {"target_interval": "S1", "count": 14, "description": "Doorstep item substitution"},
    "customer_tamper": {"target_interval": "S2", "count": 14, "description": "Customer return item replacement"},
    "reverse_transit_tamper": {"target_interval": "S3", "count": 12, "description": "Reverse transit carrier theft"},
    "degraded_evidence": {"target_interval": "S2", "count": 12, "description": "Tampered with bounding checkpoint degraded"},
    "ambiguous_evidence": {"target_interval": "S2", "count": 12, "description": "Tampered with bounding checkpoints obscured by glare"},
}


def assign_staging_cells(
    n: int = 120,
    seed: int = 42,
    output_dir: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """
    Generate randomized, sealed assignment sheet for N journeys across the 8 cells.
    Shuffles journey order with a fixed seed so no batch is homogenous.
    Writes strictly to data/restricted/.
    """
    if n != 120:
        raise ValueError(f"Amendment v2.6.0 specifies exactly N=120, received N={n}")

    rng = random.Random(seed)

    # 1. Pool cells according to quotas
    pool: List[Dict[str, str]] = []
    for cell_id, info in CELL_QUOTAS.items():
        for _ in range(info["count"]):
            pool.append({
                "assigned_cell": cell_id,
                "target_interval": info["target_interval"],
                "description": info["description"],
            })

    if len(pool) != n:
        raise ValueError(f"Cell quotas sum to {len(pool)}, expected {n}")

    # 2. Shuffle presentation order
    rng.shuffle(pool)

    # 3. Assign unique journey codes
    assignments: List[Dict[str, Any]] = []
    for idx, item in enumerate(pool, start=1):
        journey_code = f"JRN-2026-{idx:04d}"
        assignments.append({
            "order_index": idx,
            "journey_code": journey_code,
            "assigned_cell": item["assigned_cell"],
            "target_interval": item["target_interval"],
            "cell_description": item["description"],
        })

    # 4. Save to restricted directory
    target_dir = Path(output_dir) if output_dir else RESTRICTED_DATA_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    csv_path = target_dir / "staging_assignment_120.csv"
    json_path = target_dir / "staging_assignment_120.json"

    # Write CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["order_index", "journey_code", "assigned_cell", "target_interval", "cell_description"])
        writer.writeheader()
        writer.writerows(assignments)

    # Write JSON
    result = {
        "version": "2.6.0",
        "n": n,
        "seed": seed,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cell_counts": {k: v["count"] for k, v in CELL_QUOTAS.items()},
        "assignments": assignments,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")

    return {
        "csv_path": str(csv_path),
        "json_path": str(json_path),
        "n": n,
        "seed": seed,
        "sample": assignments[:3],
    }
