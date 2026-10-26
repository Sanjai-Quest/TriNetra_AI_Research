from __future__ import annotations

import pytest
from trinetra_link.attribution.policy import map_attribution_to_decision
from trinetra_link.attribution.rationale import generate_attribution_rationale


def test_policy_mapping():
    assert map_attribution_to_decision("LEGITIMATE")[0] == "DEC_REFUND"
    assert map_attribution_to_decision("STAGE(1)")[0] == "DEC_INVESTIGATE_HUB"
    assert map_attribution_to_decision("STAGE(2)")[0] == "DEC_INVESTIGATE_CARRIER"
    assert map_attribution_to_decision("STAGE(3)")[0] == "DEC_REJECT_CLAIM"
    assert map_attribution_to_decision("ABSTAIN_DEGRADED")[0] == "DEC_ESCALATE_MANUAL"
    assert map_attribution_to_decision("ABSTAIN_INDISTINGUISHABLE")[0] == "DEC_ESCALATE_MANUAL"


def test_rationale_generation():
    text = generate_attribution_rationale(
        journey_code="JRN-RAT-01",
        label="STAGE(2)",
        interval=[2, 3],
        trusted_set=[1, 2, 3, 4],
        per_modality_evidence={
            "q_k": {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
            "z_k": {1: "INTACT", 2: "INTACT", 3: "ANOM", 4: "ANOM"},
        },
        decision="DEC_INVESTIGATE_CARRIER",
    )
    assert "JRN-RAT-01" in text
    assert "STAGE(2)" in text
    assert "DEC_INVESTIGATE_CARRIER" in text
    assert "CP2 -> CP3" in text
