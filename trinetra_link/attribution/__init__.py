"""
Attribution package for TriNetra-Link.
Contains Algorithm 1 (interval.py), Bayesian attribution (bayes.py),
normative policy (policy.py), and rationale generation (rationale.py).
"""

from trinetra_link.attribution.bayes import attribute_bayes
from trinetra_link.attribution.interval import attribute_interval_algorithm_1
from trinetra_link.attribution.policy import map_attribution_to_decision
from trinetra_link.attribution.rationale import generate_attribution_rationale

__all__ = [
    "attribute_interval_algorithm_1",
    "attribute_bayes",
    "map_attribution_to_decision",
    "generate_attribution_rationale",
]
