from __future__ import annotations

from enum import Enum
from typing import List, NamedTuple, Optional, Tuple

from trinetra_link.schema.models import CheckpointObservation


class ConflictType(str, Enum):
    NONE = "NONE"
    IDENTITY_MISSING = "IDENTITY_MISSING"
    SERIAL_MISMATCH = "SERIAL_MISMATCH"
    IMEI_MISMATCH = "IMEI_MISMATCH"
    CONTINUITY_BROKEN = "CONTINUITY_BROKEN"
    MISSING_MANDATORY_EVIDENCE = "MISSING_MANDATORY_EVIDENCE"
    CUSTODY_INVALID = "CUSTODY_INVALID"
    SEAL_QR_MISMATCH = "SEAL_QR_MISMATCH"
    CONDITION_REVIEW = "CONDITION_REVIEW"


class DecisionStatus(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    HOLD = "HOLD"


class VerdictResult(NamedTuple):
    decision: DecisionStatus
    conflict_type: ConflictType
    reasoning: str


def has_text(val: Optional[str]) -> bool:
    return val is not None and len(val.strip()) > 0


def same_text(a: Optional[str], b: Optional[str]) -> bool:
    if a is None or b is None:
        return False
    return a.strip().lower() == b.strip().lower()


def evaluate_verdict_service_parity(
    expected_serial: Optional[str],
    observed_serial: Optional[str],
    expected_imei: Optional[str],
    observed_imei: Optional[str],
    is_continuity_broken: bool = False,
    mandatory_evidence_complete: bool = True,
    has_evidence_items: bool = True,
    is_custody_valid: bool = True,
    condition_status: Optional[str] = "NORMAL",
) -> VerdictResult:
    """
    Exact Python port of backend/src/main/java/com/trinetra/verdict/service/VerdictService.java.
    Evaluates identity and evidence continuity in strict priority order (Rules 1 to 6).
    """
    # Rule 1: Serial identity is incomplete
    if not has_text(expected_serial) or not has_text(observed_serial):
        return VerdictResult(
            decision=DecisionStatus.REVIEW,
            conflict_type=ConflictType.IDENTITY_MISSING,
            reasoning="Serial identity is incomplete. Expected and observed serials are required before release.",
        )

    # Rule 2: Serial mismatch
    if not same_text(expected_serial, observed_serial):
        return VerdictResult(
            decision=DecisionStatus.HOLD,
            conflict_type=ConflictType.SERIAL_MISMATCH,
            reasoning=f"Serial mismatch detected. Expected: {expected_serial}. Observed: {observed_serial}. Status: HOLD.",
        )

    # Rule 3: IMEI identity check
    if has_text(expected_imei) or has_text(observed_imei):
        if not has_text(expected_imei) or not has_text(observed_imei):
            return VerdictResult(
                decision=DecisionStatus.REVIEW,
                conflict_type=ConflictType.IDENTITY_MISSING,
                reasoning="IMEI identity is incomplete. Expected and observed IMEI are required for this unit.",
            )
        if not same_text(expected_imei, observed_imei):
            return VerdictResult(
                decision=DecisionStatus.HOLD,
                conflict_type=ConflictType.IMEI_MISMATCH,
                reasoning=f"IMEI mismatch detected. Expected: {expected_imei}. Observed: {observed_imei}. Status: HOLD.",
            )

    # Rule 4: Continuity broken
    if is_continuity_broken:
        return VerdictResult(
            decision=DecisionStatus.HOLD,
            conflict_type=ConflictType.CONTINUITY_BROKEN,
            reasoning="Checkpoint continuity failed for the serialized unit. Status: HOLD.",
        )

    # Rule 5: Mandatory verification evidence incomplete
    if not mandatory_evidence_complete or not has_evidence_items:
        return VerdictResult(
            decision=DecisionStatus.REVIEW,
            conflict_type=ConflictType.MISSING_MANDATORY_EVIDENCE,
            reasoning="Mandatory verification evidence is incomplete. Status: REVIEW.",
        )

    # Rule 6: Custody validity check
    if not is_custody_valid:
        return VerdictResult(
            decision=DecisionStatus.REVIEW,
            conflict_type=ConflictType.CUSTODY_INVALID,
            reasoning="Custody history is incomplete or inconsistent. Status: REVIEW.",
        )

    # Secondary check: Condition review
    cond = (condition_status or "").strip().upper()
    if cond in ("DAMAGED", "TAMPERED"):
        return VerdictResult(
            decision=DecisionStatus.REVIEW,
            conflict_type=ConflictType.CONDITION_REVIEW,
            reasoning=f"Identity matches. Condition is marked {cond}. Supervisor review required. Status: REVIEW.",
        )

    return VerdictResult(
        decision=DecisionStatus.PASS,
        conflict_type=ConflictType.NONE,
        reasoning="Serial matched. IMEI matched where applicable. Required evidence complete. Checkpoint continuity intact. Custody history consistent. Status: PASS.",
    )


def reconcile_identity(
    obs_baseline: CheckpointObservation,
    obs_current: CheckpointObservation,
) -> Tuple[bool, List[str]]:
    """
    Multimodal physical identity reconciliation for Checkpoint k vs CP1.
    Evaluates:
        1. Tamper-evident seal QR code
        2. Unit Serial number
        3. IMEI (if applicable)

    Returns:
        (is_identity_anomaly, list_of_mismatch_descriptions)
    """
    mismatches: List[str] = []

    # 1. Seal QR code matching
    if obs_baseline.seal_qr is not None:
        if not obs_current.seal_qr:
            mismatches.append("Seal QR missing at current checkpoint")
        elif not same_text(obs_baseline.seal_qr, obs_current.seal_qr):
            mismatches.append(f"Seal QR mismatch (expected '{obs_baseline.seal_qr}', observed '{obs_current.seal_qr}')")

    # 2. Serial number matching
    if obs_baseline.serial is not None:
        if not obs_current.serial:
            mismatches.append("Serial number missing at current checkpoint")
        elif not same_text(obs_baseline.serial, obs_current.serial):
            mismatches.append(f"Serial number mismatch (expected '{obs_baseline.serial}', observed '{obs_current.serial}')")

    # 3. IMEI matching
    if obs_baseline.imei is not None:
        if not obs_current.imei:
            mismatches.append("IMEI missing at current checkpoint")
        elif not same_text(obs_baseline.imei, obs_current.imei):
            mismatches.append(f"IMEI mismatch (expected '{obs_baseline.imei}', observed '{obs_current.imei}')")

    is_anomaly = len(mismatches) > 0
    return is_anomaly, mismatches
