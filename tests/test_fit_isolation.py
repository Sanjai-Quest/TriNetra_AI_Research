from __future__ import annotations

import pytest
from trinetra_link.fit import fit_thresholds
from trinetra_link.schema.models import Journey


def test_fit_rejects_test_split_name(tmp_path):
    with pytest.raises(ValueError, match="FITTING ISOLATION VIOLATION"):
        fit_thresholds([], split_name="test", output_dir=tmp_path)


def test_fit_rejects_test_journey_id(tmp_path):
    test_journey = Journey(
        journey_code="JRN-TEST-0042",
        status="COMPLETED",
        metadata={"split": "test"},
    )
    with pytest.raises(ValueError, match="Test journey"):
        fit_thresholds([test_journey], split_name="calibration", output_dir=tmp_path)


def test_fit_succeeds_on_calibration_split(tmp_path):
    cal_journey = Journey(
        journey_code="JRN-CALIB-001",
        status="COMPLETED",
        metadata={"split": "calibration"},
    )
    res = fit_thresholds([cal_journey], split_name="calibration", output_dir=tmp_path)
    assert res["theta"] == 0.70
    assert res["z_weight"] == 3.00
    assert res["tau_bayes"] == 0.80
    assert res["fitted_on_split"] == "calibration"
