from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from trinetra_link.config import DERIVED_DATA_DIR
from trinetra_link.schema.models import CheckpointObservation

DEFAULT_SCALES_PATH = DERIVED_DATA_DIR / "scales.json"

# Nominal default calibration parameters if scales.json is not yet generated
DEFAULT_SCALE_SIGMA_G = 0.35  # Gaussian noise standard deviation
DEFAULT_SCALE_DELTA_G = 0.10  # Maximum uncompensated linearity drift


def load_scale_parameters(
    scale_id: str,
    scales_file_path: Optional[Path | str] = None,
) -> Tuple[float, float]:
    """Retrieve scale characterization uncertainty (sigma, delta) in grams."""
    path = Path(scales_file_path) if scales_file_path else DEFAULT_SCALES_PATH
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                scales_data = json.load(f)
            scale_info = scales_data.get("scales", {}).get(scale_id, {})
            sigma = float(scale_info.get("sigma_g", DEFAULT_SCALE_SIGMA_G))
            delta = float(scale_info.get("delta_g", DEFAULT_SCALE_DELTA_G))
            return sigma, delta
        except Exception:
            pass
    return DEFAULT_SCALE_SIGMA_G, DEFAULT_SCALE_DELTA_G


def reconcile_weights(
    obs_baseline: CheckpointObservation,
    obs_current: CheckpointObservation,
    z: float = 3.0,
    scales_file_path: Optional[Path | str] = None,
    cumulative_tare_delta_g: float = 0.0,
) -> Tuple[bool, float, float]:
    """
    Evaluate weight anomaly condition:
        |w_b - w_a - tare_adj| > z * sqrt(sigma_a^2 + sigma_b^2) + delta_a + delta_b

    Tare adjustments:
        If cumulative_tare_delta_g != 0.0, it is applied directly to net weight change.
        Otherwise, point-in-time tare_delta_g is subtracted for permitted packaging changes.

    Returns:
        (is_anomaly, observed_delta_g, threshold_bound_g)
    """
    if not obs_baseline.weights_g or not obs_current.weights_g:
        return False, 0.0, 0.0

    w_a_raw = float(float(sorted(obs_baseline.weights_g)[len(obs_baseline.weights_g) // 2]))
    w_b_raw = float(float(sorted(obs_current.weights_g)[len(obs_current.weights_g) // 2]))

    # Adjust for tare modifications if logged as legitimate packaging operations
    if cumulative_tare_delta_g != 0.0:
        delta_w = abs(w_b_raw - w_a_raw - cumulative_tare_delta_g)
    else:
        w_a_adj = w_a_raw - (obs_baseline.tare_delta_g if obs_baseline.permitted_packaging_change else 0.0)
        w_b_adj = w_b_raw - (obs_current.tare_delta_g if obs_current.permitted_packaging_change else 0.0)
        delta_w = abs(w_b_adj - w_a_adj)

    sigma_a, drift_a = load_scale_parameters(obs_baseline.scale_id, scales_file_path)
    sigma_b, drift_b = load_scale_parameters(obs_current.scale_id, scales_file_path)

    sigma_comb = math.sqrt(sigma_a**2 + sigma_b**2)
    threshold_bound = z * sigma_comb + drift_a + drift_b

    is_anomaly = bool(delta_w > threshold_bound)
    return is_anomaly, round(delta_w, 4), round(threshold_bound, 4)
