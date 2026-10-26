from __future__ import annotations

import csv
from pathlib import Path
import random
from typing import Any, Dict, List, Optional, Tuple
from sklearn.metrics import cohen_kappa_score

from trinetra_link.config import RESTRICTED_DATA_DIR
from trinetra_link.staging.determinability import derive_ground_truth
from trinetra_link.staging.log import load_staging_log


def sample_journeys_for_audit(
    sample_fraction: float = 0.25,
    seed: int = 101,
    staging_log_path: Optional[Path | str] = None,
) -> List[Dict[str, Any]]:
    """Sample a random fraction of staging records for independent rule audit."""
    rows = load_staging_log(staging_log_path)
    if not rows:
        assign_csv = RESTRICTED_DATA_DIR / "staging_assignment_120.csv"
        if assign_csv.exists():
            with open(assign_csv, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                for r in rows:
                    r["manipulation_interval"] = r.get("target_interval", "none")

    if not rows:
        raise ValueError("No journeys found in data/restricted/ to sample for audit")

    rng = random.Random(seed)
    n_sample = max(1, int(len(rows) * sample_fraction))
    return rng.sample(rows, n_sample)


def compute_rule_audit_kappa(
    rater_a_labels: List[str],
    rater_b_labels: List[str],
) -> float:
    """Compute Cohen's kappa between automated rule output and auditor ratings."""
    if len(rater_a_labels) != len(rater_b_labels):
        raise ValueError("Rater label arrays must have identical length")
    if not rater_a_labels or rater_a_labels == rater_b_labels:
        return 1.0

    import numpy as np
    kappa = float(cohen_kappa_score(rater_a_labels, rater_b_labels))
    if np.isnan(kappa):
        return 1.0 if rater_a_labels == rater_b_labels else 0.0
    return round(kappa, 4)
