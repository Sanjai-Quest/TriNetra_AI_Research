"""
Quality Gate package for TriNetra-Link.
Evaluates physical capture metadata to produce q_k in [0, 1].
"""

from trinetra_link.quality.features import (
    compute_image_quality_features,
    compute_laplacian_variance_kotlin,
    evaluate_scale_readings,
    evaluate_temporal_order,
)
from trinetra_link.quality.gate import QualityGate

__all__ = [
    "QualityGate",
    "compute_laplacian_variance_kotlin",
    "compute_image_quality_features",
    "evaluate_scale_readings",
    "evaluate_temporal_order",
]
