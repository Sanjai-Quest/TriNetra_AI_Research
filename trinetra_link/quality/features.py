from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


def compute_laplacian_variance_kotlin(grayscale: np.ndarray) -> float:
    """
    Exact mathematical reproduction of Kotlin OpenCVProcessor.computeKotlinLaplacianVariance.
    Kernel: [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    Formula:
        lValue = top + bottom + left + right - 4 * center
        mean = sum(lValue) / N
        rawVariance = sum((lValue - mean)^2) / N
        return clip(rawVariance / 2500.0, 0.05, 0.95)
    """
    if grayscale.ndim != 2:
        raise ValueError("Grayscale array must be 2D")
    h, w = grayscale.shape
    if h <= 2 or w <= 2:
        return 0.25

    # Center, top, bottom, left, right slices
    center = grayscale[1:-1, 1:-1].astype(np.float64)
    top = grayscale[0:-2, 1:-1].astype(np.float64)
    bottom = grayscale[2:, 1:-1].astype(np.float64)
    left = grayscale[1:-1, 0:-2].astype(np.float64)
    right = grayscale[1:-1, 2:].astype(np.float64)

    l_values = top + bottom + left + right - 4.0 * center
    raw_variance = float(np.var(l_values))
    normalized = raw_variance / 2500.0
    return float(np.clip(normalized, 0.05, 0.95))


def compute_image_quality_features(
    image_bgr: np.ndarray,
    exif_exposure: Optional[float] = None,
) -> Dict[str, float]:
    """Compute photographic quality features without inspecting parcel state."""
    import cv2

    h, w = image_bgr.shape[:2]
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    mean_luminance = float(np.mean(gray))
    laplacian_var = compute_laplacian_variance_kotlin(gray)

    # Specular highlights: high Value (V > 240) and low Saturation (S < 30)
    specular_mask = (hsv[:, :, 2] > 240) & (hsv[:, :, 1] < 30)
    specular_fraction = float(np.count_nonzero(specular_mask) / (h * w))

    # Lux proxy from exposure if present
    lux_proxy = 1.0
    if exif_exposure is not None and exif_exposure > 0:
        # Relative brightness index proxy: mean luminance / exposure_time
        lux_proxy = float(np.clip(mean_luminance / (exif_exposure * 1000.0), 0.1, 10.0))

    return {
        "width": float(w),
        "height": float(h),
        "mean_luminance": mean_luminance,
        "laplacian_variance": laplacian_var,
        "specular_fraction": specular_fraction,
        "lux_proxy": lux_proxy,
    }


def evaluate_scale_readings(
    weights_g: List[float],
    scale_status: str,
    min_readings: int = 3,
    min_weight_g: float = 1.0,
    max_spread_g: float = 2.0,
    allowed_statuses: Optional[List[str]] = None,
) -> Tuple[float, List[str]]:
    """Evaluate repeated scale reading spread, status, and validity."""
    reasons: List[str] = []
    if allowed_statuses is None:
        allowed_statuses = ["OK", "MANUAL", "SETTLED"]

    # Status check
    status_upper = scale_status.upper().strip()
    if status_upper not in allowed_statuses:
        reasons.append(f"Scale status '{scale_status}' is unpermitted/unsettled")
        return 0.0, reasons

    # Reading count check
    if len(weights_g) < min_readings:
        reasons.append(f"Expected >= {min_readings} repeated weighings, got {len(weights_g)}")
        return 0.0, reasons

    # Zero or negative reading check
    min_reading = min(weights_g)
    if min_reading < min_weight_g:
        reasons.append(f"Minimum reading {min_reading:.2f}g is below floor {min_weight_g:.2f}g")
        return 0.0, reasons

    # Spread check
    spread = max(weights_g) - min(weights_g)
    if spread > max_spread_g:
        spread_score = max(0.0, 1.0 - (spread - max_spread_g) / max_spread_g)
        reasons.append(f"Scale spread {spread:.2f}g exceeds threshold {max_spread_g:.2f}g")
        return spread_score, reasons

    return 1.0, reasons


def evaluate_temporal_order(
    current_ts: datetime,
    prev_ts: Optional[datetime],
    calibration_date_str: Optional[str] = None,
    max_cal_age_days: int = 365,
) -> Tuple[float, List[str]]:
    """Evaluate timestamp chronological order and calibration age."""
    reasons: List[str] = []
    score = 1.0

    if prev_ts is not None:
        if current_ts <= prev_ts:
            reasons.append(f"Checkpoint timestamp {current_ts} is not strictly after previous {prev_ts}")
            return 0.0, reasons

    if calibration_date_str:
        try:
            cal_date = datetime.strptime(calibration_date_str.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            # Compare with current_ts (make timezone-aware if needed)
            ref_ts = current_ts if current_ts.tzinfo else current_ts.replace(tzinfo=timezone.utc)
            age_days = (ref_ts - cal_date).days
            if age_days > max_cal_age_days:
                reasons.append(f"Scale calibration age ({age_days} days) exceeds limit ({max_cal_age_days} days)")
                score = max(0.0, 1.0 - (age_days - max_cal_age_days) / max_cal_age_days)
            elif age_days < 0:
                reasons.append("Scale calibration date is in the future")
                score = 0.5
        except Exception:
            reasons.append(f"Malformed calibration date '{calibration_date_str}'")
            score = 0.5

    return score, reasons
