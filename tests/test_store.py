from __future__ import annotations

from datetime import datetime, timezone
import pytest
from trinetra_link.schema.models import CheckpointObservation, Journey
from trinetra_link.store.database import Store


def test_store_journey_and_checkpoint_append_only(tmp_path):
    db_file = tmp_path / "test_store.sqlite"
    store = Store(db_file)

    j = Journey(journey_code="JRN-STORE-01", status="ACTIVE")
    store.insert_journey(j)

    # Re-inserting the same journey must fail (append-only)
    with pytest.raises(ValueError):
        store.insert_journey(j)

    cp1 = CheckpointObservation(
        journey_code="JRN-STORE-01",
        cp_index=1,
        ts_utc=datetime.now(timezone.utc),
        device_id="DEV-01",
        operator_id="OP-01",
        weights_g=[500.0, 500.1, 500.0],
        scale_id="SCALE-01",
        scale_status="OK",
    )
    store.insert_checkpoint(cp1)

    # Re-inserting CP1 must fail (append-only)
    with pytest.raises(ValueError):
        store.insert_checkpoint(cp1)

    cps = store.list_checkpoints("JRN-STORE-01")
    assert len(cps) == 1
    assert cps[0].journey_code == "JRN-STORE-01"
    assert cps[0].weights_g == [500.0, 500.1, 500.0]
