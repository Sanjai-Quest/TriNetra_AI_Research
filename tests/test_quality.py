from __future__ import annotations

from datetime import datetime, timezone, timedelta
import numpy as np
import pytest
from trinetra_link.quality.features import (
    compute_image_quality_features,
    evaluate_scale_readings,
    evaluate_temporal_order,
)
from trinetra_link.quality.gate import QualityGate
from trinetra_link.schema.models import CheckpointObservation, ImageRef


def test_scale_reading_evaluation_clean():
    score, reasons = evaluate_scale_readings(
        weights_g=[500.1, 500.2, 500.1],
        scale_status="OK",
    )
    assert score == 1.0
    assert len(reasons) == 0


def test_scale_reading_evaluation_unstable_spread():
    # Spread is 5.0g > max_spread 2.0g
    score, reasons = evaluate_scale_readings(
        weights_g=[500.0, 505.0, 502.0],
        scale_status="OK",
        max_spread_g=2.0,
    )
    assert score < 1.0
    assert any("spread" in r for r in reasons)


def test_scale_reading_evaluation_error_status():
    score, reasons = evaluate_scale_readings(
        weights_g=[500.0, 500.0, 500.0],
        scale_status="ERROR",
    )
    assert score == 0.0
    assert any("unpermitted" in r for r in reasons)


def test_scale_reading_min_weight_floor():
    score, reasons = evaluate_scale_readings(
        weights_g=[0.0, 0.0, 0.0],
        scale_status="OK",
        min_weight_g=1.0,
    )
    assert score == 0.0
    assert any("floor" in r for r in reasons)


def test_scale_reading_insufficient_repeats():
    score, reasons = evaluate_scale_readings(
        weights_g=[500.0],
        scale_status="OK",
        min_readings=3,
    )
    assert score == 0.0
    assert any("Expected >=" in r for r in reasons)


def test_temporal_evaluation_inverted_timestamp():
    t1 = datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 10, 26, 10, 0, 0, tzinfo=timezone.utc)  # inverted!
    score, reasons = evaluate_temporal_order(current_ts=t2, prev_ts=t1)
    assert score == 0.0
    assert any("not strictly after" in r for r in reasons)


def test_temporal_calibration_dates():
    now = datetime(2026, 10, 26, 12, 0, 0, tzinfo=timezone.utc)

    # Valid recent calibration
    score, reasons = evaluate_temporal_order(now, None, calibration_date_str="2026-05-01")
    assert score == 1.0
    assert len(reasons) == 0

    # Expired calibration (> 365 days)
    score_exp, reasons_exp = evaluate_temporal_order(now, None, calibration_date_str="2024-01-01", max_cal_age_days=365)
    assert score_exp < 1.0
    assert any("exceeds limit" in r for r in reasons_exp)

    # Future calibration date
    score_fut, reasons_fut = evaluate_temporal_order(now, None, calibration_date_str="2027-01-01")
    assert score_fut == 0.5

    # Malformed calibration date
    score_bad, _ = evaluate_temporal_order(now, None, calibration_date_str="invalid-date")
    assert score_bad == 0.5


def test_compute_image_quality_features():
    # Synthetic BGR image (100x100)
    img = np.full((100, 100, 3), 120, dtype=np.uint8)
    # Add high specular glare region
    img[0:20, 0:20] = [255, 255, 255]

    feats = compute_image_quality_features(img, exif_exposure=0.02)
    assert feats["width"] == 100.0
    assert feats["height"] == 100.0
    assert feats["mean_luminance"] > 100.0
    assert feats["specular_fraction"] > 0.0
    assert feats["lux_proxy"] > 0.0


def test_quality_gate_with_image_pixel_arrays():
    gate = QualityGate(theta=0.70)
    obs = CheckpointObservation(
        journey_code="JRN-IMG-01",
        cp_index=1,
        ts_utc=datetime.now(timezone.utc),
        device_id="DEV-01",
        operator_id="OP-01",
        weights_g=[350.0, 350.1, 350.0],
        scale_id="SCALE-01",
        scale_status="OK",
        images=[
            ImageRef(side="front", path="mock_front.png", sha256="fake", w=800, h=600)
        ]
    )

    # 1. Good image array with sharp grid texture
    good_img = np.full((600, 800, 3), 120, dtype=np.uint8)
    good_img[::4, ::4] = 60
    good_img[1::4, 1::4] = 180
    report_good = gate.evaluate(obs, image_arrays={"front": good_img})
    assert report_good.q_k >= 0.70
    assert report_good.passed

    # 2. Dark image array
    dark_img = np.full((600, 800, 3), 10, dtype=np.uint8)
    report_dark = gate.evaluate(obs, image_arrays={"front": dark_img})
    assert any("underexposed" in r for r in report_dark.reasons)

    # 3. Overexposed image array
    bright_img = np.full((600, 800, 3), 250, dtype=np.uint8)
    report_bright = gate.evaluate(obs, image_arrays={"front": bright_img})
    assert any("overexposed" in r for r in report_bright.reasons)
