from __future__ import annotations

from datetime import datetime, timezone
import pytest
from trinetra_link.reconcile.fuse import fuse_checkpoint_observations
from trinetra_link.schema.models import CheckpointObservation, QualityReport


def make_obs(cp: int, weights: list[float], qr: str = "SEAL-1") -> CheckpointObservation:
    return CheckpointObservation(
        journey_code="JRN-FUSE-01",
        cp_index=cp,
        ts_utc=datetime.now(timezone.utc),
        device_id="DEV-01",
        operator_id="OP-01",
        weights_g=weights,
        scale_id="SCALE-STD",
        scale_status="OK",
        seal_qr=qr,
        serial="SN-100",
    )


def test_fuse_all_trusted_agree_yields_intact():
    obs_a = make_obs(1, [500.0, 500.0, 500.0])
    obs_b = make_obs(2, [500.1, 500.0, 500.1])
    qr = QualityReport(
        journey_code="JRN-FUSE-01",
        cp_index=2,
        q_k=0.95,
        feature_scores={"q_scale": 1.0, "q_temporal": 1.0, "q_image": 1.0},
        passed=True,
    )
    res = fuse_checkpoint_observations(obs_a, obs_b, qr)
    assert res.fused_state == "INTACT"


def test_fuse_weight_anomaly_in_trusted_yields_anom():
    obs_a = make_obs(1, [500.0, 500.0, 500.0])
    obs_b = make_obs(2, [450.0, 450.0, 450.0])  # 50g loss
    qr = QualityReport(
        journey_code="JRN-FUSE-01",
        cp_index=2,
        q_k=0.95,
        feature_scores={"q_scale": 1.0, "q_temporal": 1.0, "q_image": 1.0},
        passed=True,
    )
    res = fuse_checkpoint_observations(obs_a, obs_b, qr)
    assert res.fused_state == "ANOM"
    assert res.weight_anomaly


def test_fuse_identity_anomaly_in_trusted_yields_anom():
    obs_a = make_obs(1, [500.0, 500.0, 500.0], qr="SEAL-ORIG")
    obs_b = make_obs(2, [500.0, 500.0, 500.0], qr="SEAL-TAMPERED")
    qr = QualityReport(
        journey_code="JRN-FUSE-01",
        cp_index=2,
        q_k=0.95,
        feature_scores={"q_scale": 1.0, "q_temporal": 1.0, "q_image": 1.0},
        passed=True,
    )
    res = fuse_checkpoint_observations(obs_a, obs_b, qr)
    assert res.fused_state == "ANOM"
    assert res.identity_anomaly


def test_fuse_untrusted_modalities_yields_unk():
    obs_a = make_obs(1, [500.0, 500.0, 500.0])
    obs_b = make_obs(2, [450.0, 450.0, 450.0])
    # Everything untrusted (e.g. scale error, temporal inversion, etc.)
    qr = QualityReport(
        journey_code="JRN-FUSE-01",
        cp_index=2,
        q_k=0.20,
        feature_scores={"q_scale": 0.1, "q_temporal": 0.1, "q_image": 0.1},
        passed=False,
    )
    res = fuse_checkpoint_observations(obs_a, obs_b, qr, theta=0.70)
    assert res.fused_state == "UNK"
