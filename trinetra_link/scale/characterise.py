from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

from trinetra_link.config import DERIVED_DATA_DIR

DEFAULT_SCALES_JSON = DERIVED_DATA_DIR / "scales.json"


def record_reference_readings(
    scale_id: str,
    nominal_load_g: float,
    readings: List[float],
    log_dir: Optional[Path | str] = None,
) -> Path:
    """Record calibration readings for a specific reference mass."""
    target_dir = Path(log_dir) if log_dir else DERIVED_DATA_DIR / "scale_calibration"
    target_dir.mkdir(parents=True, exist_ok=True)

    out_file = target_dir / f"{scale_id}_load_{int(nominal_load_g)}g.json"
    record = {
        "scale_id": scale_id,
        "nominal_load_g": nominal_load_g,
        "readings_count": len(readings),
        "readings": readings,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    return out_file


def fit_scale_model(
    reference_loads: Dict[float, List[float]],
) -> Dict[str, float]:
    """
    Fit empirical Gaussian noise standard deviation sigma and drift delta.
    - sigma: Pooled standard deviation of readings around reference mean
    - delta: Maximum systematic linearity offset |mean(w) - nominal|
    """
    variances = []
    offsets = []

    for nominal, readings in reference_loads.items():
        if len(readings) < 3:
            raise ValueError(f"Each reference load requires >= 3 readings, got {len(readings)} for {nominal}g")
        arr = np.array(readings, dtype=np.float64)
        mean_val = float(np.mean(arr))
        var_val = float(np.var(arr, ddof=1)) if len(arr) > 1 else 0.0
        variances.append(var_val)
        offsets.append(abs(mean_val - nominal))

    # Pooled standard deviation
    pooled_sigma = float(np.sqrt(np.mean(variances)))
    # Maximum linearity drift
    max_drift = float(np.max(offsets))

    return {
        "sigma_g": round(max(pooled_sigma, 0.01), 4),
        "delta_g": round(max_drift, 4),
    }


def characterise_scale(
    scale_id: str,
    reference_loads: Dict[float, List[float]],
    output_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """
    Fit and persist scale parameters to data/derived/scales.json.
    """
    if len(reference_loads) < 3:
        raise ValueError(f"Scale characterisation requires >= 3 reference loads, got {len(reference_loads)}")

    fit_res = fit_scale_model(reference_loads)

    out_path = Path(output_path) if output_path else DEFAULT_SCALES_JSON
    out_path.parent.mkdir(parents=True, exist_ok=True)

    scales_data: Dict[str, Any] = {"version": "2.6.0", "scales": {}}
    if out_path.exists():
        try:
            with open(out_path, "r", encoding="utf-8") as f:
                scales_data = json.load(f)
        except Exception:
            pass

    scales_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    scales_data["scales"][scale_id] = {
        "sigma_g": fit_res["sigma_g"],
        "delta_g": fit_res["delta_g"],
        "reference_loads_g": sorted(list(reference_loads.keys())),
        "readings_per_load": [len(r) for r in reference_loads.values()],
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(scales_data, f, indent=2)
        f.write("\n")

    return scales_data["scales"][scale_id]
