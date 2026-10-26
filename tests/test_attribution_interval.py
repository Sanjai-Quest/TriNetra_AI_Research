from __future__ import annotations

import pytest
from trinetra_link.attribution.interval import attribute_interval_algorithm_1


def test_cp1_untrusted_yields_abstain_degraded():
    # 1 not in T
    q_k = {1: 0.40, 2: 0.95, 3: 0.95, 4: 0.95}
    z_k = {1: "INTACT", 2: "INTACT", 3: "INTACT", 4: "INTACT"}
    res = attribute_interval_algorithm_1("TEST-01", q_k, z_k, theta=0.70)
    assert res.label == "ABSTAIN_DEGRADED"
    assert "CP1" in res.rationale_text


def test_no_anomalies_terminal_trusted_yields_legitimate():
    # A is empty, K=4 in T
    q_k = {1: 0.95, 2: 0.90, 3: 0.85, 4: 0.92}
    z_k = {1: "INTACT", 2: "INTACT", 3: "INTACT", 4: "INTACT"}
    res = attribute_interval_algorithm_1("TEST-02", q_k, z_k, theta=0.70)
    assert res.label == "LEGITIMATE"
    assert res.interval == [1, 4]


def test_no_anomalies_terminal_untrusted_yields_abstain_degraded():
    # A is empty, but K=4 not in T
    q_k = {1: 0.95, 2: 0.90, 3: 0.85, 4: 0.50}
    z_k = {1: "INTACT", 2: "INTACT", 3: "INTACT", 4: "INTACT"}
    res = attribute_interval_algorithm_1("TEST-03", q_k, z_k, theta=0.70)
    assert res.label == "ABSTAIN_DEGRADED"
    assert "destination CP4" in res.rationale_text


def test_stage_1_resolution():
    # b = 2, a = 1 -> STAGE(1)
    q_k = {1: 0.95, 2: 0.90, 3: 0.85, 4: 0.92}
    z_k = {1: "INTACT", 2: "ANOM", 3: "ANOM", 4: "ANOM"}
    res = attribute_interval_algorithm_1("TEST-04", q_k, z_k, theta=0.70)
    assert res.label == "STAGE(1)"
    assert res.interval == [1, 2]


def test_stage_2_resolution():
    # b = 3, a = 2 -> STAGE(2)
    q_k = {1: 0.95, 2: 0.90, 3: 0.85, 4: 0.92}
    z_k = {1: "INTACT", 2: "INTACT", 3: "ANOM", 4: "ANOM"}
    res = attribute_interval_algorithm_1("TEST-05", q_k, z_k, theta=0.70)
    assert res.label == "STAGE(2)"
    assert res.interval == [2, 3]


def test_stage_3_resolution():
    # b = 4, a = 3 -> STAGE(3)
    q_k = {1: 0.95, 2: 0.90, 3: 0.85, 4: 0.92}
    z_k = {1: "INTACT", 2: "INTACT", 3: "INTACT", 4: "ANOM"}
    res = attribute_interval_algorithm_1("TEST-06", q_k, z_k, theta=0.70)
    assert res.label == "STAGE(3)"
    assert res.interval == [3, 4]


def test_dryrun07_pattern_intermediate_degraded():
    # DRYRUN-07: CP1, CP2 intact. CP3 dark with scale error (q3 = 0.10). CP4 anom.
    # a = 2, b = 4. Intervening CP3 has q3 < theta -> ABSTAIN_DEGRADED.
    q_k = {1: 0.95, 2: 0.92, 3: 0.10, 4: 0.90}
    z_k = {1: "INTACT", 2: "INTACT", 3: "UNK", 4: "ANOM"}
    res = attribute_interval_algorithm_1("TEST-DRYRUN07", q_k, z_k, theta=0.70)
    assert res.label == "ABSTAIN_DEGRADED"
    assert res.interval == [2, 4]
    assert 3 in res.per_modality_evidence["degraded_in_interval"]


def test_intermediate_unk_trusted_yields_abstain_indistinguishable():
    # CP1 intact. CP2 has q2 >= theta but state UNK. CP3 anom.
    # b = 3, a = 1. Intervening CP2 was checked (q2 >= theta), but b != a + 1 -> ABSTAIN_INDISTINGUISHABLE.
    q_k = {1: 0.95, 2: 0.85, 3: 0.90, 4: 0.92}
    z_k = {1: "INTACT", 2: "UNK", 3: "ANOM", 4: "ANOM"}
    res = attribute_interval_algorithm_1("TEST-08", q_k, z_k, theta=0.70)
    assert res.label == "ABSTAIN_INDISTINGUISHABLE"
    assert res.interval == [1, 3]
