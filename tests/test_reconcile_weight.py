from __future__ import annotations

import json
from datetime import datetime, timezone
import pytest
from trinetra_link.reconcile.weight import load_scale_parameters, reconcile_weights
from trinetra_link.schema.models import CheckpointObservation


def make_obs(cp: int, weights: list[float], permitted: bool = False, tare: float = 0.0) -> CheckpointObservation:
    return CheckpointObservation(
        journey_code="JRN-TEST-WT",
        cp_index=cp,
        ts_utc=datetime.now(timezone.utc),
        device_id="DEV-01",
        operator_id="OP-01",
        weights_g=weights,
        scale_id="SCALE-STD",
        scale_status="OK",
        permitted_packaging_change=permitted,
        tare_delta_g=tare,
    )


def test_weight_intact_within_noise_bound():
    obs_a = make_obs(1, [500.0, 500.1, 499.9])
    obs_b = make_obs(2, [500.2, 500.1, 500.2])
    # Delta is ~0.1g, well below bound z * sqrt(2 * 0.35^2) + 0.20 ~= 1.68g
    is_anom, delta_w, bound = reconcile_weights(obs_a, obs_b, z=3.0)
    assert not is_anom
    assert delta_w < bound


def test_weight_anomaly_detected():
    obs_a = make_obs(1, [500.0, 500.1, 500.0])
    obs_b = make_obs(2, [485.0, 485.1, 484.9])  # 15g loss
    is_anom, delta_w, bound = reconcile_weights(obs_a, obs_b, z=3.0)
    assert is_anom
    assert delta_w > bound


def test_tare_adjustment_compensates_legitimate_change():
    # Package had 20g of legitimate extra protective tape added at hub
    obs_a = make_obs(1, [500.0, 500.0, 500.0])
    obs_b = make_obs(2, [520.1, 520.0, 520.1], permitted=True, tare=20.0)
    is_anom, delta_w, bound = reconcile_weights(obs_a, obs_b, z=3.0)
    # Tare-adjusted weight is 500.0 vs 500.0 -> intact
    assert not is_anom
    assert delta_w < bound


def test_load_scale_parameters_from_file(tmp_path):
    scales_json_file = tmp_path / "scales.json"
    scales_data = {
        "scales": {
            "SCALE-PRECISION-01": {"sigma_g": 0.05, "delta_g": 0.01}
        }
    }
    with open(scales_json_file, "w", encoding="utf-8") as f:
        json.dump(scales_data, f)

    sigma, delta = load_scale_parameters("SCALE-PRECISION-01", scales_file_path=scales_json_file)
    assert sigma == 0.05
    assert delta == 0.01

    # Missing scale falls back to defaults
    sigma_def, delta_def = load_scale_parameters("NONEXISTENT", scales_file_path=scales_json_file)
    assert sigma_def == 0.35
    assert delta_def == 0.10


def test_missing_weights_returns_unknown():
    """When either baseline or current checkpoint has no weights, return UNKNOWN."""
    obs_valid = make_obs(1, [500.0, 500.1, 500.0])
    obs_empty = make_obs(2, [])

    # Case A: Current checkpoint has empty weights
    status_a, delta_a, bound_a = reconcile_weights(obs_valid, obs_empty)
    assert status_a == "UNKNOWN"
    assert delta_a == 0.0

    # Case B: Baseline checkpoint has empty weights
    status_b, delta_b, bound_b = reconcile_weights(obs_empty, obs_valid)
    assert status_b == "UNKNOWN"
    assert delta_b == 0.0

    # Case C: Both checkpoints have empty weights
    status_c, delta_c, bound_c = reconcile_weights(obs_empty, obs_empty)
    assert status_c == "UNKNOWN"
    assert delta_c == 0.0

