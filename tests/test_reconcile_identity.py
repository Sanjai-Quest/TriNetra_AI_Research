from __future__ import annotations

from datetime import datetime, timezone
import pytest
from trinetra_link.reconcile.identity import reconcile_identity
from trinetra_link.schema.models import CheckpointObservation


def make_obs(cp: int, qr: str = "SEAL-1", serial: str = "SN-1", imei: str = "IMEI-1") -> CheckpointObservation:
    return CheckpointObservation(
        journey_code="JRN-TEST-ID",
        cp_index=cp,
        ts_utc=datetime.now(timezone.utc),
        device_id="DEV-01",
        operator_id="OP-01",
        weights_g=[500.0, 500.0, 500.0],
        scale_id="SCALE-STD",
        scale_status="OK",
        seal_qr=qr,
        serial=serial,
        imei=imei,
    )


def test_reconcile_identity_matches_cleanly():
    obs_a = make_obs(1)
    obs_b = make_obs(2)
    is_anom, mismatches = reconcile_identity(obs_a, obs_b)
    assert not is_anom
    assert len(mismatches) == 0


def test_reconcile_identity_detects_seal_tamper():
    obs_a = make_obs(1, qr="SEAL-ORIGINAL")
    obs_b = make_obs(2, qr="SEAL-REPLACED")
    is_anom, mismatches = reconcile_identity(obs_a, obs_b)
    assert is_anom
    assert any("Seal QR" in m for m in mismatches)


def test_reconcile_identity_detects_serial_mismatch():
    obs_a = make_obs(1, serial="SN-GENUINE")
    obs_b = make_obs(2, serial="SN-COUNTERFEIT")
    is_anom, mismatches = reconcile_identity(obs_a, obs_b)
    assert is_anom
    assert any("Serial number" in m for m in mismatches)
