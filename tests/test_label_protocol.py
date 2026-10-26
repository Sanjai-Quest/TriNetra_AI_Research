from __future__ import annotations

from datetime import datetime, timezone
import pytest
from typing import Dict, List

from trinetra_link.attribution.interval import attribute_interval_algorithm_1
from trinetra_link.attribution.bayes import attribute_bayes
from trinetra_link.baselines.b1_cp4 import predict_b1_cp4
from trinetra_link.baselines.b2_endpoints import predict_b2_endpoints
from trinetra_link.baselines.b3_unlinked import predict_b3_unlinked
from trinetra_link.baselines.b4_llm_judge import predict_b4_llm_judge
from trinetra_link.baselines.b5_v3_rules import predict_b5_v3_rules
from trinetra_link.schema.models import CheckpointObservation, Journey

PROTOCOL_LABELS = {
    "ATTR_CONFIRMED_LEGITIMATE",
    "ATTR_STAGE(1)",
    "ATTR_STAGE(2)",
    "ATTR_STAGE(3)",
    "ATTR_ABSTAIN_DEGRADED",
    "ATTR_ABSTAIN_INDISTINGUISHABLE",
}


def make_synthetic_test_journey(
    tamper_checkpoint: int = 0,
    weights: List[float] = [500.0, 500.0, 500.0],
    seal: str = "SEAL-OK",
    quality_good: bool = True,
) -> Journey:
    """Helper to create test journey with controlled parameters."""
    cps = []
    for k in (1, 2, 3, 4):
        is_tampered = tamper_checkpoint > 0 and k >= tamper_checkpoint
        cp_weights = [w - 30.0 for w in weights] if is_tampered else list(weights)
        cp_seal = "SEAL-BROKEN" if is_tampered else seal
        scale_status = "OK" if quality_good else "ERROR"
        cps.append(
            CheckpointObservation(
                journey_code="JRN-TEST-PROTO",
                cp_index=k,
                ts_utc=datetime.now(timezone.utc),
                device_id=f"DEV_CP{k}",
                operator_id=f"OP_CP{k}",
                weights_g=cp_weights,
                scale_id="SCALE_STD",
                scale_status=scale_status,
                seal_qr=cp_seal,
                serial="SN-12345",
                imei="354892019283741",
            )
        )
    return Journey(journey_code="JRN-TEST-PROTO", checkpoints=cps)


def test_every_method_emits_valid_protocol_labels():
    """Ensure every attribution method and baseline outputs strictly valid protocol labels."""
    test_cases = [
        # Legitimate intact
        make_synthetic_test_journey(tamper_checkpoint=0),
        # Tamper at CP2 -> Stage 1
        make_synthetic_test_journey(tamper_checkpoint=2),
        # Tamper at CP3 -> Stage 2
        make_synthetic_test_journey(tamper_checkpoint=3),
        # Tamper at CP4 -> Stage 3
        make_synthetic_test_journey(tamper_checkpoint=4),
        # Degraded
        make_synthetic_test_journey(tamper_checkpoint=0, quality_good=False),
    ]

    for j in test_cases:
        # 1. Algorithm 1
        q_k = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}
        z_k = {1: "INTACT", 2: "INTACT", 3: "INTACT", 4: "INTACT"}
        res_alg1 = attribute_interval_algorithm_1(j.journey_code, q_k, z_k)
        assert res_alg1.label in PROTOCOL_LABELS, f"Algorithm 1 emitted non-protocol label: {res_alg1.label}"

        # 2. Bayes
        res_bayes = attribute_bayes(j.journey_code, q_k, z_k)
        assert res_bayes.label in PROTOCOL_LABELS, f"Bayes emitted non-protocol label: {res_bayes.label}"

        # 3. Baselines B1..B5
        b1 = predict_b1_cp4(j)
        assert b1.label in PROTOCOL_LABELS, f"B1 emitted non-protocol label: {b1.label}"

        b2 = predict_b2_endpoints(j)
        assert b2.label in PROTOCOL_LABELS, f"B2 emitted non-protocol label: {b2.label}"

        b3 = predict_b3_unlinked(j)
        assert b3.label in PROTOCOL_LABELS, f"B3 emitted non-protocol label: {b3.label}"

        b4 = predict_b4_llm_judge(j)
        assert b4.label in PROTOCOL_LABELS, f"B4 emitted non-protocol label: {b4.label}"

        b5 = predict_b5_v3_rules(j)
        assert b5.label in PROTOCOL_LABELS, f"B5 emitted non-protocol label: {b5.label}"


def test_property_alg1_equals_b3_when_all_checkpoints_trusted():
    """
    Property test: when all four checkpoints are trusted (q_k >= theta for all k in 1..4),
    Algorithm 1 and Baseline B3 must return the exact same stage attribution.
    """
    q_trusted = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}

    # Test all possible monotonic anomaly injection points (CP2, CP3, CP4, or None)
    scenarios = [
        # (tamper_cp, expected_stage)
        (0, "ATTR_CONFIRMED_LEGITIMATE"),
        (2, "ATTR_STAGE(1)"),
        (3, "ATTR_STAGE(2)"),
        (4, "ATTR_STAGE(3)"),
    ]

    for tamper_cp, expected_label in scenarios:
        j = make_synthetic_test_journey(tamper_checkpoint=tamper_cp)
        
        # Physical anomaly states for Alg 1 corresponding to tamper point
        z_k = {1: "INTACT"}
        for k in (2, 3, 4):
            z_k[k] = "ANOM" if (tamper_cp > 0 and k >= tamper_cp) else "INTACT"

        alg1_attr = attribute_interval_algorithm_1(j.journey_code, q_trusted, z_k)
        b3_attr = predict_b3_unlinked(j)

        assert alg1_attr.label == expected_label, (
            f"Alg 1 expected {expected_label}, got {alg1_attr.label}"
        )
        assert b3_attr.label == expected_label, (
            f"B3 expected {expected_label}, got {b3_attr.label}"
        )
        assert alg1_attr.label == b3_attr.label, (
            f"Alg 1 ({alg1_attr.label}) != B3 ({b3_attr.label}) for tamper at CP{tamper_cp}"
        )
