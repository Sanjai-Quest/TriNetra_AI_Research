from __future__ import annotations

import numpy as np
from typing import Optional
from trinetra_link.schema.models import Attribution, CheckpointObservation, Journey


def predict_b2_endpoints(journey: Journey) -> Attribution:
    """
    Baseline B2: CP1 + CP4 Endpoints Comparison.
    Compares the origin intake (CP1) directly against the destination return hub (CP4),
    ignoring all intermediate transit checkpoints (CP2, CP3).
    When an endpoint discrepancy is detected, cannot distinguish S1 vs S2 vs S3;
    attributes coarsely to the journey endpoint span or terminal default S3.
    """
    code = journey.journey_code
    cp1: Optional[CheckpointObservation] = None
    cp4: Optional[CheckpointObservation] = None

    for cp in journey.checkpoints:
        if cp.cp_index == 1:
            cp1 = cp
        elif cp.cp_index == 4:
            cp4 = cp

    if cp1 is None or cp4 is None:
        return Attribution(
            journey_code=code,
            label="ATTR_ABSTAIN_DEGRADED",
            rationale_text="Baseline B2: One or both endpoint checkpoints (CP1, CP4) are missing.",
        )

    tare_delta = sum(cp.tare_delta_g for cp in journey.checkpoints if cp.permitted_packaging_change)

    w1 = float(np.mean(cp1.weights_g)) if cp1.weights_g else 0.0
    w4 = float(np.mean(cp4.weights_g)) if cp4.weights_g else 0.0
    weight_diff = abs(w4 - w1 - tare_delta)

    # Identity check between endpoints
    seal_diff = bool(cp1.seal_qr and cp4.seal_qr and cp1.seal_qr != cp4.seal_qr)
    serial_diff = bool(cp1.serial and cp4.serial and cp1.serial != cp4.serial)
    imei_diff = bool(cp1.imei and cp4.imei and cp1.imei != cp4.imei)

    anomalous = (weight_diff > 2.0) or seal_diff or serial_diff or imei_diff

    if anomalous:
        # Endpoints comparison cannot localize intermediate stage:
        # Heuristic predicts S3 (or coarse unlocalized discrepancy)
        return Attribution(
            journey_code=code,
            label="ATTR_STAGE_REVERSE_TRANSIT",
            interval=[1, 4],
            rationale_text=(
                f"Baseline B2: Endpoint discrepancy detected between CP1 and CP4 "
                f"(delta_weight={weight_diff:.2f}g, seal_diff={seal_diff}, serial_diff={serial_diff}). "
                f"Intermediate stages unobserved; defaulted to terminal stage S3."
            ),
        )

    return Attribution(
        journey_code=code,
        label="ATTR_CONFIRMED_LEGITIMATE",
        interval=[1, 4],
        rationale_text="Baseline B2: Endpoints CP1 and CP4 match within tolerance; classified as legitimate.",
    )
