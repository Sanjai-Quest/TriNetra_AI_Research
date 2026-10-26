from __future__ import annotations

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from trinetra_link.schema.models import CheckpointObservation, Journey, QualityReport


def test_checkpoint_negative_weight_rejected():
    with pytest.raises(ValidationError):
        CheckpointObservation(
            journey_code="JRN-FAIL-01",
            cp_index=1,
            ts_utc=datetime.now(timezone.utc),
            device_id="DEV-01",
            operator_id="OP-01",
            weights_g=[-5.0, 500.0, 500.0],  # Negative weight!
            scale_id="SCALE-01",
            scale_status="OK",
        )


def test_checkpoint_cp_index_out_of_bounds_rejected():
    with pytest.raises(ValidationError):
        CheckpointObservation(
            journey_code="JRN-FAIL-02",
            cp_index=0,  # Must be >= 1
            ts_utc=datetime.now(timezone.utc),
            device_id="DEV-01",
            operator_id="OP-01",
            weights_g=[500.0, 500.0, 500.0],
            scale_id="SCALE-01",
            scale_status="OK",
        )


def test_journey_model_dump_and_reload():
    j = Journey(
        journey_code="JRN-OK-01",
        status="ACTIVE",
        metadata={"carrier": "Bluedart", "priority": "high"},
    )
    data = j.model_dump()
    j_reloaded = Journey(**data)
    assert j_reloaded.journey_code == "JRN-OK-01"
    assert j_reloaded.metadata["carrier"] == "Bluedart"
