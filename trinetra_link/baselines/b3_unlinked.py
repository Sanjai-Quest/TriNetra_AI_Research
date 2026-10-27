from __future__ import annotations

import numpy as np
from typing import Optional
from trinetra_link.schema.models import Attribution, CheckpointObservation, Journey


def predict_b3_unlinked(journey: Journey) -> Attribution:
    """
    Baseline B3: All Signals Unlinked ('Detection = Origin').
    Evaluates checkpoints independently against origin CP1.
    Attributes the disruption to the stage ending at the first checkpoint where an anomaly is detected:
      - Anomaly at CP2 -> Stage S1 (between CP1 and CP2)
      - Anomaly at CP3 -> Stage S2 (between CP2 and CP3)
      - Anomaly at CP4 -> Stage S3 (between CP3 and CP4)
    Does not gate evidence quality or verify bounding checkpoint integrity (never abstains on degraded evidence).
    """
    code = journey.journey_code
    cps_by_index: dict[int, CheckpointObservation] = {cp.cp_index: cp for cp in journey.checkpoints}
    cp1 = cps_by_index.get(1)

    if cp1 is None:
        return Attribution(
            journey_code=code,
            label="ATTR_ABSTAIN_DEGRADED",
            rationale_text="Baseline B3: Missing origin baseline checkpoint CP1.",
        )

    w1 = float(np.mean(cp1.weights_g)) if cp1.weights_g else 0.0

    for k in (2, 3, 4):
        cp_k = cps_by_index.get(k)
        if cp_k is None:
            continue

        # Cumulative permitted tare changes up to k
        tare_k = sum(
            cp.tare_delta_g
            for cp in journey.checkpoints
            if cp.cp_index <= k and cp.permitted_packaging_change
        )

        w_k = float(np.mean(cp_k.weights_g)) if cp_k.weights_g else 0.0
        weight_diff = abs(w_k - w1 - tare_k)

        is_weight_anomaly = (weight_diff > 2.0)
        is_seal_anomaly = bool(cp1.seal_qr and cp_k.seal_qr and cp1.seal_qr != cp_k.seal_qr)
        is_serial_anomaly = bool(cp1.serial and cp_k.serial and cp1.serial != cp_k.serial)
        is_imei_anomaly = bool(cp1.imei and cp_k.imei and cp1.imei != cp_k.imei)

        if is_weight_anomaly or is_seal_anomaly or is_serial_anomaly or is_imei_anomaly:
            stage_idx = k - 1
            stage_map = {
                1: "ATTR_STAGE_FORWARD_TRANSIT",
                2: "ATTR_STAGE_CONSUMER_CUSTODY",
                3: "ATTR_STAGE_REVERSE_TRANSIT",
            }
            stage_label = stage_map.get(stage_idx, f"ATTR_STAGE_{stage_idx}")
            return Attribution(
                journey_code=code,
                label=stage_label,
                interval=[stage_idx, stage_idx + 1],
                rationale_text=(
                    f"Baseline B3 (Detection=Origin): Earliest anomaly detected at CP{k} "
                    f"(weight_diff={weight_diff:.2f}g, seal_diff={is_seal_anomaly}, "
                    f"serial_diff={is_serial_anomaly}). Attributed to preceding Stage {stage_label}."
                ),
            )

    return Attribution(
        journey_code=code,
        label="ATTR_CONFIRMED_LEGITIMATE",
        interval=[1, 4],
        rationale_text="Baseline B3: No checkpoint exhibited anomaly above threshold; classified as legitimate.",
    )
