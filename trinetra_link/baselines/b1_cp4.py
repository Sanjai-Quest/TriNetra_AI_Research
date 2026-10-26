from __future__ import annotations

import numpy as np
from typing import Any, Dict, Optional
from trinetra_link.schema.models import Attribution, CheckpointObservation, Journey


def predict_b1_cp4(journey: Journey) -> Attribution:
    """
    Baseline B1: CP4-Only Terminal Rule.
    Only evaluates the terminal destination checkpoint CP4.
    If CP4 exhibits weight anomaly, seal alteration, or scale error, flags tampering.
    Without earlier checkpoints, cannot resolve origin; attributes terminal stage ATTR_STAGE(3).
    If CP4 is clean, attributes ATTR_CONFIRMED_LEGITIMATE.
    """
    code = journey.journey_code
    cp4: Optional[CheckpointObservation] = None
    cp1: Optional[CheckpointObservation] = None

    for cp in journey.checkpoints:
        if cp.cp_index == 4:
            cp4 = cp
        elif cp.cp_index == 1:
            cp1 = cp

    if cp4 is None:
        return Attribution(
            journey_code=code,
            label="ATTR_ABSTAIN_DEGRADED",
            rationale_text="Baseline B1: Terminal checkpoint CP4 is missing from journey telemetry.",
        )

    # Reference tare/nominal adjustment
    tare_delta = sum(cp.tare_delta_g for cp in journey.checkpoints if cp.permitted_packaging_change)

    # Check CP4 scale status
    if cp4.scale_status in ("ERROR", "UNSTABLE"):
        return Attribution(
            journey_code=code,
            label="ATTR_STAGE(3)",
            interval=[3, 4],
            rationale_text="Baseline B1: CP4 recorded scale error status; terminal anomaly flagged.",
        )

    # Weight comparison vs CP1 or nominal
    w4 = float(np.mean(cp4.weights_g)) if cp4.weights_g else 0.0
    w1 = float(np.mean(cp1.weights_g)) if cp1 and cp1.weights_g else w4

    weight_diff = abs(w4 - w1 - tare_delta)
    is_weight_anomaly = weight_diff > 2.0

    # Seal comparison vs CP1
    is_seal_anomaly = False
    if cp1 and cp1.seal_qr and cp4.seal_qr:
        is_seal_anomaly = (cp1.seal_qr != cp4.seal_qr)

    if is_weight_anomaly or is_seal_anomaly:
        return Attribution(
            journey_code=code,
            label="ATTR_STAGE(3)",
            interval=[3, 4],
            rationale_text=(
                f"Baseline B1: Terminal anomaly detected at CP4 (weight_diff={weight_diff:.2f}g, "
                f"seal_anomaly={is_seal_anomaly}). Attributed to terminal stage S3."
            ),
        )

    return Attribution(
        journey_code=code,
        label="ATTR_CONFIRMED_LEGITIMATE",
        interval=[1, 4],
        rationale_text="Baseline B1: Terminal checkpoint CP4 matches baseline; classified as legitimate.",
    )
