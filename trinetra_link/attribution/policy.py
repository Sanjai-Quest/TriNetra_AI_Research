from __future__ import annotations

from typing import Tuple


def map_attribution_to_decision(label: str, confidence: float = 1.0) -> Tuple[str, str]:
    """
    Normative operational policy mapping:
        Maps (attribution_label, confidence) -> (decision_code, explanation)
    Kept strictly decoupled from attribution algorithms.
    """
    lbl = label.upper().strip()

    if lbl == "LEGITIMATE":
        return (
            "DEC_REFUND",
            "Physical integrity intact throughout journey. Approve claim / release payment."
        )
    elif lbl == "STAGE(1)":
        return (
            "DEC_INVESTIGATE_HUB",
            "Tamper isolated to Stage 1 (origin dispatch / first hub). Open carrier and facility audit."
        )
    elif lbl == "STAGE(2)":
        return (
            "DEC_INVESTIGATE_CARRIER",
            "Tamper isolated to Stage 2 (line-haul / hub transit). File claim against primary transit carrier."
        )
    elif lbl == "STAGE(3)":
        return (
            "DEC_REJECT_CLAIM",
            "Tamper isolated to Stage 3 (last-mile / doorstep delivery). Reject claim due to doorstep substitution."
        )
    elif lbl == "ABSTAIN_DEGRADED":
        return (
            "DEC_ESCALATE_MANUAL",
            "Observation evidence degraded or untrusted. Escalate to senior physical investigation team."
        )
    elif lbl == "ABSTAIN_INDISTINGUISHABLE":
        return (
            "DEC_ESCALATE_MANUAL",
            "Intervening physical evidence unresolvable across stages. Escalate for manual custody reconciliation."
        )
    else:
        return (
            "DEC_HOLD",
            f"Unrecognized attribution label '{label}'. Place journey on investigative hold."
        )
