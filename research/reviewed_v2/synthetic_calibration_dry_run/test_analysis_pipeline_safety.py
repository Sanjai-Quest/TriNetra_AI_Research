"""
TriNetra AI: Synthetic Pipeline Safety & Reliability Test Fixture
Protocol Version: 2.5.0 (Synthetic Rehearsal Mode)

Verifies that the Fleiss' Kappa analysis implementation:
1. Calculates attribution-assessment Fleiss' kappa separately from operational decisions.
2. Rejects incomplete, malformed, or blank input templates.
3. Rejects invalid categorical values.
4. Produces deterministic, reproducible numerical outputs.
5. Matches an exact independently hand-calculated benchmark (kappa = 7/11 = 0.6364).

DISCLAIMER: SYNTHETIC DATA ONLY. DOES NOT MODIFY OFFICIAL AUDIT DATA.
"""

import os
import sys
import numpy as np
import pandas as pd

# Add parent directory to path to test the official compute_calibration_agreement module
PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from compute_calibration_agreement import (
    compute_fleiss_kappa,
    evaluate_calibration_ratings,
    ALLOWED_ATTRIBUTIONS,
    ALLOWED_DECISIONS,
)

def test_metric_separation():
    print("=== TEST 1: Metric Separation Test ===")
    synthetic_csv = os.path.join(os.path.dirname(__file__), "synthetic_agent_results.csv")
    df = pd.read_csv(synthetic_csv)
    
    attr_res = compute_fleiss_kappa(df, 'attribution_assessment', ALLOWED_ATTRIBUTIONS)
    dec_res = compute_fleiss_kappa(df, 'operational_decision', ALLOWED_DECISIONS)
    
    assert 'kappa' in attr_res and 'kappa' in dec_res
    assert attr_res['kappa'] != dec_res['kappa'], "Metrics must not be identical or conflated"
    assert attr_res['k'] == len(ALLOWED_ATTRIBUTIONS)
    assert dec_res['k'] == len(ALLOWED_DECISIONS)
    print(f"PASSED: Attribution kappa ({attr_res['kappa']:.4f}) and Decision kappa ({dec_res['kappa']:.4f}) calculated independently.\n")

def test_input_rejection():
    print("=== TEST 2: Input Rejection of Blank / Malformed Data ===")
    base_dir = os.path.dirname(__file__)
    
    # 1. Blank template rejection
    archive_template = os.path.join(PARENT_DIR, "..", "archive", "e3_reviewer_gate", "calibration_ratings_template.csv")
    blank_template = archive_template if os.path.exists(archive_template) else os.path.join(PARENT_DIR, "calibration_ratings_template.csv")
    result = evaluate_calibration_ratings(blank_template)
    assert result is False, "Empty template must be rejected with False"
    print("Assertion Passed: Blank template correctly rejected.")
    
    # 2. Incomplete / partially filled CSV rejection
    partial_csv = os.path.join(base_dir, "test_temp_partial.csv")
    df_partial = pd.DataFrame({
        "case_id": ["DRYRUN-01", "DRYRUN-01", "DRYRUN-01", "DRYRUN-01"],
        "reviewer_id": ["R1", "R2", "R3", "R4"],
        "attribution_assessment": ["ATTR_CONFIRMED_LEGITIMATE", "ATTR_CONFIRMED_LEGITIMATE", None, "ATTR_CONFIRMED_LEGITIMATE"],
        "operational_decision": ["DEC_APPROVE_REFUND", "DEC_APPROVE_REFUND", "DEC_APPROVE_REFUND", "DEC_APPROVE_REFUND"],
    })
    df_partial.to_csv(partial_csv, index=False)
    partial_res = evaluate_calibration_ratings(partial_csv)
    assert partial_res is False, "Partial template with nulls must be rejected"
    os.remove(partial_csv)
    print("Assertion Passed: Partial ratings with missing values correctly rejected.")
    
    # 3. Invalid category rejection
    df_invalid = pd.DataFrame({
        "case_id": ["DRYRUN-01", "DRYRUN-01", "DRYRUN-01", "DRYRUN-01"],
        "reviewer_id": ["R1", "R2", "R3", "R4"],
        "attribution_assessment": ["ATTR_CONFIRMED_LEGITIMATE", "ATTR_INVALID_CATEGORY_NAME", "ATTR_CONFIRMED_LEGITIMATE", "ATTR_CONFIRMED_LEGITIMATE"],
        "operational_decision": ["DEC_APPROVE_REFUND", "DEC_APPROVE_REFUND", "DEC_APPROVE_REFUND", "DEC_APPROVE_REFUND"],
    })
    try:
        compute_fleiss_kappa(df_invalid, 'attribution_assessment', ALLOWED_ATTRIBUTIONS)
        assert False, "Failed to reject invalid category"
    except ValueError as e:
        assert "Invalid category value" in str(e)
        print("Assertion Passed: Invalid category value raised ValueError as expected.")
        
    # 4. Duplicate assessment rejection
    df_duplicate = pd.DataFrame({
        "case_id": ["DRYRUN-01", "DRYRUN-01", "DRYRUN-01", "DRYRUN-01"],
        "reviewer_id": ["R1", "R1", "R3", "R4"], # R1 duplicated
        "attribution_assessment": ["ATTR_CONFIRMED_LEGITIMATE"] * 4,
        "operational_decision": ["DEC_APPROVE_REFUND"] * 4,
    })
    try:
        compute_fleiss_kappa(df_duplicate, 'attribution_assessment', ALLOWED_ATTRIBUTIONS)
        assert False, "Failed to reject duplicate assessment"
    except ValueError as e:
        assert "Duplicate assessment found" in str(e)
        print("Assertion Passed: Duplicate assessment raised ValueError as expected.")

    # 5. Imbalanced design rejection
    df_imbalanced = pd.DataFrame({
        "case_id": ["CASE-1", "CASE-1", "CASE-1", "CASE-2"],
        "reviewer_id": ["R1", "R2", "R3", "R1"],
        "attribution_assessment": ["ATTR_CONFIRMED_LEGITIMATE"] * 4,
        "operational_decision": ["DEC_APPROVE_REFUND"] * 4,
    })
    try:
        compute_fleiss_kappa(df_imbalanced, 'attribution_assessment', ALLOWED_ATTRIBUTIONS)
        assert False, "Failed to reject imbalanced design"
    except ValueError as e:
        assert "Imbalanced design" in str(e) or "Incomplete ratings" in str(e)
        print("Assertion Passed: Imbalanced rating counts raised ValueError as expected.")
        
    # 6. Missing reviewer count rejection
    df_3reviewers = pd.DataFrame({
        "case_id": ["C01", "C01", "C01"],
        "reviewer_id": ["R1", "R2", "R3"],
        "attribution_assessment": ["ATTR_CONFIRMED_LEGITIMATE"] * 3,
        "operational_decision": ["DEC_APPROVE_REFUND"] * 3,
    })
    test_3rev_csv = os.path.join(base_dir, "test_temp_3rev.csv")
    df_3reviewers.to_csv(test_3rev_csv, index=False)
    res_3rev = evaluate_calibration_ratings(test_3rev_csv)
    assert res_3rev is False, "Dataset with fewer than 4 reviewers must be rejected"
    os.remove(test_3rev_csv)
    print("Assertion Passed: Fewer than 4 reviewers rejected with False.")

    print("TEST 2 PASSED: All malformed, invalid, duplicate, and imbalanced inputs successfully rejected.\n")

def test_numerical_reproducibility():
    print("=== TEST 3: Numerical Reproducibility Test ===")
    synthetic_csv = os.path.join(os.path.dirname(__file__), "synthetic_agent_results.csv")
    df = pd.read_csv(synthetic_csv)
    
    res1 = compute_fleiss_kappa(df, 'attribution_assessment', ALLOWED_ATTRIBUTIONS)
    res2 = compute_fleiss_kappa(df, 'attribution_assessment', ALLOWED_ATTRIBUTIONS)
    
    assert abs(res1['kappa'] - res2['kappa']) < 1e-12, "Calculation must be 100% deterministic"
    assert abs(res1['P_bar'] - res2['P_bar']) < 1e-12
    assert abs(res1['P_bar_e'] - res2['P_bar_e']) < 1e-12
    print(f"PASSED: Determinism verified. Run 1 = Run 2 = {res1['kappa']:.10f}\n")

def test_hand_calculated_benchmark():
    print("=== TEST 4: Independently Verified Hand-Calculated Mathematical Benchmark ===")
    # Construct exact 3-case, 4-rater, 3-category example:
    # Case 1: [4, 0, 0]
    # Case 2: [0, 4, 0]
    # Case 3: [2, 0, 2]
    # N=3, m=4, k=3
    # Hand calculation:
    # p_j = [6/12, 4/12, 2/12] = [0.5, 1/3, 1/6]
    # P_1 = (16-4)/12 = 1.0
    # P_2 = (16-4)/12 = 1.0
    # P_3 = (4+0+4-4)/12 = 4/12 = 1/3
    # P_bar = (1 + 1 + 1/3)/3 = 7/9 ≈ 0.7777778
    # P_bar_e = 0.5^2 + (1/3)^2 + (1/6)^2 = 1/4 + 1/9 + 1/36 = 14/36 = 7/18 ≈ 0.3888889
    # kappa = (7/9 - 7/18) / (1 - 7/18) = (7/18) / (11/18) = 7/11 ≈ 0.6363636364
    
    benchmark_df = pd.DataFrame({
        "case_id": ["CASE-1"]*4 + ["CASE-2"]*4 + ["CASE-3"]*4,
        "reviewer_id": ["R1", "R2", "R3", "R4"]*3,
        "attribution_assessment": [
            "CAT_A", "CAT_A", "CAT_A", "CAT_A",
            "CAT_B", "CAT_B", "CAT_B", "CAT_B",
            "CAT_A", "CAT_A", "CAT_C", "CAT_C"
        ]
    })
    
    benchmark_categories = ["CAT_A", "CAT_B", "CAT_C"]
    res = compute_fleiss_kappa(benchmark_df, 'attribution_assessment', benchmark_categories)
    
    expected_P_bar = 7.0 / 9.0
    expected_P_bar_e = 7.0 / 18.0
    expected_kappa = 7.0 / 11.0
    
    print(f"Hand-Calculated Expected: P_bar={expected_P_bar:.6f}, P_bar_e={expected_P_bar_e:.6f}, kappa={expected_kappa:.6f}")
    print(f"Algorithm Output:         P_bar={res['P_bar']:.6f}, P_bar_e={res['P_bar_e']:.6f}, kappa={res['kappa']:.6f}")
    
    assert abs(res['P_bar'] - expected_P_bar) < 1e-9, f"P_bar mismatch: {res['P_bar']} vs {expected_P_bar}"
    assert abs(res['P_bar_e'] - expected_P_bar_e) < 1e-9, f"P_bar_e mismatch: {res['P_bar_e']} vs {expected_P_bar_e}"
    assert abs(res['kappa'] - expected_kappa) < 1e-9, f"Kappa mismatch: {res['kappa']} vs {expected_kappa}"
    
    print("TEST 4 PASSED: Algorithm matches exact analytical benchmark (kappa = 7/11 = 0.636364).\n")

def main():
    print("=====================================================================")
    print("   TRINETRA AI: SYNTHETIC PIPELINE SAFETY & VERIFICATION SUITE       ")
    print("=====================================================================\n")
    test_metric_separation()
    test_input_rejection()
    test_numerical_reproducibility()
    test_hand_calculated_benchmark()
    print("ALL 4 SYNTHETIC PIPELINE SAFETY TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    main()
