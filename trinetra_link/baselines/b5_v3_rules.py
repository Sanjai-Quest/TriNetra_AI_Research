from __future__ import annotations

import numpy as np
from typing import Optional
from trinetra_link.reconcile.identity import ConflictType, DecisionStatus, evaluate_verdict_service_parity
from trinetra_link.schema.models import Attribution, CheckpointObservation, Journey


def predict_b5_v3_rules(journey: Journey) -> Attribution:
    """
    Baseline B5: Ported V3 Heuristic Rules (VerdictService.java & fixed 2.0g threshold).
    Applies legacy rule hierarchy across checkpoints:
      1. Priority identity rules 1-6 (serial mismatch, IMEI mismatch, missing identity).
      2. Fixed uncalibrated 2.0g weight threshold.
      3. Security seal string match.
    Attributes to the stage where the rule condition first triggers.
    Does not perform Bayesian quality weighting or quality gate interval bounding.
    """
    code = journey.journey_code
    cps = {cp.cp_index: cp for cp in journey.checkpoints}
    cp1 = cps.get(1)

    if not cp1 or len(cps) < 4:
        return Attribution(
            journey_code=code,
            label="ATTR_ABSTAIN_DEGRADED",
            rationale_text="Baseline B5: Incomplete checkpoint sequence (missing CP1 or fewer than 4 checkpoints).",
        )

    w1 = float(np.mean(cp1.weights_g)) if cp1.weights_g else 0.0

    for k in (2, 3, 4):
        cp_k = cps.get(k)
        if not cp_k:
            continue

        # 1. Identity Parity Rules (VerdictService rules 1..6)
        identity_verdict = evaluate_verdict_service_parity(
            expected_serial=cp1.serial,
            observed_serial=cp_k.serial,
            expected_imei=cp1.imei,
            observed_imei=cp_k.imei,
            is_continuity_broken=False,
            mandatory_evidence_complete=bool(cp_k.images),
            has_evidence_items=bool(cp_k.images),
            is_custody_valid=True,
            condition_status="NORMAL",
        )

        is_identity_conflict = (identity_verdict.decision in (DecisionStatus.HOLD, DecisionStatus.REVIEW))
        if identity_verdict.conflict_type in (ConflictType.SERIAL_MISMATCH, ConflictType.IMEI_MISMATCH):
            stage = k - 1
            return Attribution(
                journey_code=code,
                label=f"ATTR_STAGE({stage})",
                interval=[stage, stage + 1],
                rationale_text=(
                    f"Baseline B5 Rule Conflict at CP{k}: {identity_verdict.conflict_type.value} "
                    f"triggered stage attribution S{stage}."
                ),
            )

        # 2. Seal QR string match
        if cp1.seal_qr and cp_k.seal_qr and cp1.seal_qr != cp_k.seal_qr:
            stage = k - 1
            return Attribution(
                journey_code=code,
                label=f"ATTR_STAGE({stage})",
                interval=[stage, stage + 1],
                rationale_text=f"Baseline B5 Seal Mismatch at CP{k}: attributed to stage S{stage}.",
            )

        # 3. Fixed un-calibrated 2.0g weight threshold
        tare_k = sum(
            cp.tare_delta_g
            for cp in journey.checkpoints
            if cp.cp_index <= k and cp.permitted_packaging_change
        )
        w_k = float(np.mean(cp_k.weights_g)) if cp_k.weights_g else 0.0
        if abs(w_k - w1 - tare_k) > 2.0:
            stage = k - 1
            return Attribution(
                journey_code=code,
                label=f"ATTR_STAGE({stage})",
                interval=[stage, stage + 1],
                rationale_text=f"Baseline B5 Fixed 2g Weight Anomaly at CP{k}: attributed to stage S{stage}.",
            )

    return Attribution(
        journey_code=code,
        label="ATTR_CONFIRMED_LEGITIMATE",
        interval=[1, 4],
        rationale_text="Baseline B5: All V3 rules satisfied across all checkpoints; classified as legitimate.",
    )
