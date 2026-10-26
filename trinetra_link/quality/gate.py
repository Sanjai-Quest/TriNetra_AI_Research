from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

from trinetra_link.config import load_quality_config
from trinetra_link.quality.features import (
    compute_image_quality_features,
    evaluate_scale_readings,
    evaluate_temporal_order,
)
from trinetra_link.schema.models import CheckpointObservation, QualityReport


class QualityGate:
    """
    Evaluates physical observation telemetry and photographic metadata to produce
    a non-negative trust factor q_k in [0, 1]. Reads metadata only, never ground truth.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, theta: float = 0.70):
        self.config = config or load_quality_config()
        self.theta = theta

    def evaluate(
        self,
        observation: CheckpointObservation,
        previous_observation: Optional[CheckpointObservation] = None,
        image_arrays: Optional[Dict[str, np.ndarray]] = None,
    ) -> QualityReport:
        cfg = self.config
        img_cfg = cfg.get("image", {})
        scale_cfg = cfg.get("scale", {})
        temp_cfg = cfg.get("temporal", {})

        reasons: List[str] = []
        feature_scores: Dict[str, float] = {}

        # 1. Scale Telemetry Gate
        q_scale, scale_reasons = evaluate_scale_readings(
            weights_g=observation.weights_g,
            scale_status=observation.scale_status,
            min_readings=scale_cfg.get("min_readings", 3),
            min_weight_g=scale_cfg.get("min_weight_g", 1.0),
            max_spread_g=scale_cfg.get("max_spread_g", 2.0),
            allowed_statuses=scale_cfg.get("allowed_statuses", ["OK", "MANUAL", "SETTLED"]),
        )
        feature_scores["q_scale"] = q_scale
        reasons.extend(scale_reasons)

        # 2. Temporal Continuity & Calibration Gate
        prev_ts = previous_observation.ts_utc if previous_observation else None
        q_temp, temp_reasons = evaluate_temporal_order(
            current_ts=observation.ts_utc,
            prev_ts=prev_ts,
            calibration_date_str=observation.calibration_date,
            max_cal_age_days=temp_cfg.get("max_calibration_age_days", 365),
        )
        feature_scores["q_temporal"] = q_temp
        reasons.extend(temp_reasons)

        # 3. Photographic Asset Metadata Gates
        q_image = 1.0
        if observation.images:
            image_scores: List[float] = []
            for img_ref in observation.images:
                # Resolution check
                w_ok = img_ref.w >= img_cfg.get("min_width", 640)
                h_ok = img_ref.h >= img_cfg.get("min_height", 480)
                res_score = 1.0 if (w_ok and h_ok) else min(
                    img_ref.w / img_cfg.get("min_width", 640),
                    img_ref.h / img_cfg.get("min_height", 480),
                )
                feature_scores[f"q_res_{img_ref.side}"] = res_score

                # Image pixels check if image array is passed or exists
                img_arr = None
                if image_arrays and img_ref.side in image_arrays:
                    img_arr = image_arrays[img_ref.side]
                elif Path(img_ref.path).exists():
                    import cv2
                    img_arr = cv2.imread(str(img_ref.path))

                if img_arr is not None:
                    feats = compute_image_quality_features(img_arr, exif_exposure=img_ref.exposure)
                    # Luminance gate
                    lum = feats["mean_luminance"]
                    min_l = img_cfg.get("min_luminance", 30.0)
                    max_l = img_cfg.get("max_luminance", 240.0)
                    if lum < min_l:
                        lum_score = max(0.0, lum / min_l)
                        reasons.append(f"Image '{img_ref.side}' underexposed / dark (lum={lum:.1f})")
                    elif lum > max_l:
                        lum_score = max(0.0, (255.0 - lum) / (255.0 - max_l))
                        reasons.append(f"Image '{img_ref.side}' overexposed (lum={lum:.1f})")
                    else:
                        lum_score = 1.0

                    # Sharpness / Laplacian variance gate
                    lap_var = feats["laplacian_variance"]
                    min_lap = img_cfg.get("min_laplacian_variance", 0.10)
                    if lap_var < min_lap:
                        sharp_score = max(0.0, lap_var / min_lap)
                        reasons.append(f"Image '{img_ref.side}' blurry / out of focus (lap_var={lap_var:.3f})")
                    else:
                        sharp_score = 1.0

                    # Specular highlight gate
                    spec = feats["specular_fraction"]
                    max_spec = img_cfg.get("max_specular_fraction", 0.15)
                    if spec > max_spec:
                        spec_score = max(0.0, 1.0 - (spec - max_spec) / (1.0 - max_spec))
                        reasons.append(f"Image '{img_ref.side}' high specular glare ({spec * 100:.1f}%)")
                    else:
                        spec_score = 1.0

                    img_combined = res_score * lum_score * sharp_score * spec_score
                    feature_scores[f"q_lum_{img_ref.side}"] = lum_score
                    feature_scores[f"q_sharp_{img_ref.side}"] = sharp_score
                    feature_scores[f"q_spec_{img_ref.side}"] = spec_score
                    image_scores.append(img_combined)
                else:
                    # Without pixel array available, rely on resolution
                    image_scores.append(res_score)

            if image_scores:
                # Geometric mean across sides
                q_image = float(np.prod(image_scores) ** (1.0 / len(image_scores)))
        feature_scores["q_image"] = q_image

        # Overall multiplicative quality score
        q_k = float(np.clip(q_scale * q_temp * q_image, 0.0, 1.0))
        passed = bool(q_k >= self.theta)

        return QualityReport(
            journey_code=observation.journey_code,
            cp_index=observation.cp_index,
            q_k=round(q_k, 4),
            feature_scores=feature_scores,
            passed=passed,
            reasons=reasons,
        )
