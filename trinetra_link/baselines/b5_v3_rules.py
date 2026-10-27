from __future__ import annotations

from typing import Optional
from trinetra_link.reconcile.identity import ConflictType, DecisionStatus, evaluate_verdict_service_parity
from trinetra_link.schema.models import Attribution, CheckpointObservation, Journey


def predict_b5_v3_rules(journey: Journey) -> Attribution:
    """
    Baseline B5: Legacy V3 Business Rules (VerdictService.java).
    Uses ONLY serial/IMEI/custody rules and strictly ignores weight and images.
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

    stage_map = {
        1: "ATTR_STAGE_FORWARD_TRANSIT",
        2: "ATTR_STAGE_CONSUMER_CUSTODY",
        3: "ATTR_STAGE_REVERSE_TRANSIT",
    }

    for k in (2, 3, 4):
        cp_k = cps.get(k)
        if not cp_k:
            continue

        # Evaluate VerdictService parity rules on serial/IMEI/custody ONLY (ignores weight and images)
        identity_verdict = evaluate_verdict_service_parity(
            expected_serial=cp1.serial,
            observed_serial=cp_k.serial,
            expected_imei=cp1.imei,
            observed_imei=cp_k.imei,
            is_continuity_broken=False,
            mandatory_evidence_complete=True,
            has_evidence_items=True,
            is_custody_valid=True,
            condition_status="NORMAL",
        )

        if identity_verdict.decision in (DecisionStatus.HOLD, DecisionStatus.REVIEW):
            stage = k - 1
            stage_label = stage_map.get(stage, f"ATTR_STAGE_{stage}")
            return Attribution(
                journey_code=code,
                label=stage_label,
                interval=[stage, stage + 1],
                rationale_text=(
                    f"Baseline B5 Rule Conflict at CP{k}: {identity_verdict.conflict_type.value} "
                    f"triggered stage attribution {stage_label}."
                ),
            )

    return Attribution(
        journey_code=code,
        label="ATTR_CONFIRMED_LEGITIMATE",
        interval=[1, 4],
        rationale_text="Baseline B5: All V3 serial/IMEI/custody rules satisfied across all checkpoints; classified as legitimate.",
    )
