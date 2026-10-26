"""
Scale characterisation module for TriNetra-Link (Phase C).
Computes empirical noise sigma and linearity drift delta per digital scale.
"""

from trinetra_link.scale.characterise import (
    characterise_scale,
    fit_scale_model,
    record_reference_readings,
)

__all__ = [
    "characterise_scale",
    "record_reference_readings",
    "fit_scale_model",
]
