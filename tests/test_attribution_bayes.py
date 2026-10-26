from __future__ import annotations

import pytest
from trinetra_link.attribution.bayes import STAGES, attribute_bayes


def test_qk_zero_makes_checkpoint_uninformative():
    """When q_k = 0, changing the observation at k has zero effect on the posterior."""
    q_base = {1: 1.0, 2: 1.0, 3: 0.0, 4: 1.0}

    # Case A: CP3 is ANOM
    z_a = {1: "INTACT", 2: "INTACT", 3: "ANOM", 4: "ANOM"}
    res_a = attribute_bayes("TEST-Q0-A", q_base, z_a, tau=0.80)

    # Case B: CP3 is INTACT
    z_b = {1: "INTACT", 2: "INTACT", 3: "INTACT", 4: "ANOM"}
    res_b = attribute_bayes("TEST-Q0-B", q_base, z_b, tau=0.80)

    # Posteriors must be exactly equal
    for s in STAGES:
        assert pytest.approx(res_a.posterior[s], abs=1e-5) == res_b.posterior[s]


def test_posterior_monotonicity_in_qk():
    """Increasing q_k for a diagnostic checkpoint monotonically increases the target stage posterior."""
    # Observations indicate ATTR_STAGE(1): CP1 intact, CP2..CP4 anom
    z_k = {1: "INTACT", 2: "ANOM", 3: "ANOM", 4: "ANOM"}

    posteriors = []
    for q2 in [0.1, 0.3, 0.6, 0.9]:
        q_k = {1: 1.0, 2: q2, 3: 0.5, 4: 0.5}
        res = attribute_bayes("TEST-MONO", q_k, z_k, tau=0.50)
        posteriors.append(res.posterior["ATTR_STAGE(1)"])

    # Strict monotonic increase
    for i in range(len(posteriors) - 1):
        assert posteriors[i] < posteriors[i + 1]


def test_confident_posterior_resolution():
    q_k = {1: 0.95, 2: 0.95, 3: 0.95, 4: 0.95}
    z_k = {1: "INTACT", 2: "INTACT", 3: "ANOM", 4: "ANOM"}
    res = attribute_bayes("TEST-CONF", q_k, z_k, tau=0.80)
    assert res.label == "ATTR_STAGE(2)"
    assert res.posterior["ATTR_STAGE(2)"] >= 0.80
    assert res.interval == [2, 3]


def test_unconfident_posterior_abstains():
    # Fluctuation / contradictory observations
    q_k = {1: 0.30, 2: 0.30, 3: 0.30, 4: 0.30}
    z_k = {1: "UNK", 2: "UNK", 3: "UNK", 4: "UNK"}
    res = attribute_bayes("TEST-LOW", q_k, z_k, tau=0.80, theta=0.70)
    assert res.label == "ATTR_ABSTAIN_DEGRADED"
