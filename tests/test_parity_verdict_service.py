from __future__ import annotations

import pytest
from trinetra_link.reconcile.identity import (
    ConflictType,
    DecisionStatus,
    evaluate_verdict_service_parity,
)


def test_rule1_serial_missing():
    # Rule 1: Expected or observed serial missing -> REVIEW / IDENTITY_MISSING
    res = evaluate_verdict_service_parity(
        expected_serial=None,
        observed_serial="SN-12345",
        expected_imei="IMEI-001",
        observed_imei="IMEI-001",
    )
    assert res.decision == DecisionStatus.REVIEW
    assert res.conflict_type == ConflictType.IDENTITY_MISSING


def test_rule2_serial_mismatch_overrides_subsequent_rules():
    # Rule 2: Serial mismatch -> HOLD / SERIAL_MISMATCH (even if IMEI or continuity also broken)
    res = evaluate_verdict_service_parity(
        expected_serial="SN-12345",
        observed_serial="SN-99999",
        expected_imei="IMEI-001",
        observed_imei="IMEI-MISMATCH",
        is_continuity_broken=True,
    )
    assert res.decision == DecisionStatus.HOLD
    assert res.conflict_type == ConflictType.SERIAL_MISMATCH


def test_rule3_imei_missing_and_mismatch():
    # Rule 3a: IMEI incomplete
    res_inc = evaluate_verdict_service_parity(
        expected_serial="SN-12345",
        observed_serial="SN-12345",
        expected_imei="IMEI-001",
        observed_imei="",
    )
    assert res_inc.decision == DecisionStatus.REVIEW
    assert res_inc.conflict_type == ConflictType.IDENTITY_MISSING

    # Rule 3b: IMEI mismatch
    res_mis = evaluate_verdict_service_parity(
        expected_serial="SN-12345",
        observed_serial="SN-12345",
        expected_imei="IMEI-001",
        observed_imei="IMEI-999",
    )
    assert res_mis.decision == DecisionStatus.HOLD
    assert res_mis.conflict_type == ConflictType.IMEI_MISMATCH


def test_rule4_continuity_broken():
    # Rule 4: Continuity broken -> HOLD / CONTINUITY_BROKEN
    res = evaluate_verdict_service_parity(
        expected_serial="SN-12345",
        observed_serial="SN-12345",
        expected_imei="IMEI-001",
        observed_imei="IMEI-001",
        is_continuity_broken=True,
    )
    assert res.decision == DecisionStatus.HOLD
    assert res.conflict_type == ConflictType.CONTINUITY_BROKEN


def test_rule5_missing_mandatory_evidence():
    # Rule 5: Evidence incomplete -> REVIEW / MISSING_MANDATORY_EVIDENCE
    res = evaluate_verdict_service_parity(
        expected_serial="SN-12345",
        observed_serial="SN-12345",
        expected_imei="IMEI-001",
        observed_imei="IMEI-001",
        mandatory_evidence_complete=False,
    )
    assert res.decision == DecisionStatus.REVIEW
    assert res.conflict_type == ConflictType.MISSING_MANDATORY_EVIDENCE


def test_rule6_custody_invalid():
    # Rule 6: Custody invalid -> REVIEW / CUSTODY_INVALID
    res = evaluate_verdict_service_parity(
        expected_serial="SN-12345",
        observed_serial="SN-12345",
        expected_imei="IMEI-001",
        observed_imei="IMEI-001",
        is_custody_valid=False,
    )
    assert res.decision == DecisionStatus.REVIEW
    assert res.conflict_type == ConflictType.CUSTODY_INVALID


def test_clean_journey_passes():
    # All match -> PASS / NONE
    res = evaluate_verdict_service_parity(
        expected_serial="SN-12345",
        observed_serial="SN-12345",
        expected_imei="IMEI-001",
        observed_imei="IMEI-001",
        is_continuity_broken=False,
        mandatory_evidence_complete=True,
        has_evidence_items=True,
        is_custody_valid=True,
        condition_status="NORMAL",
    )
    assert res.decision == DecisionStatus.PASS
    assert res.conflict_type == ConflictType.NONE
