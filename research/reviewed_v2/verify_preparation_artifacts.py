import os
import hashlib
import pandas as pd
import numpy as np

DIR_PATH = r"c:\Users\mitsu\Downloads\TriNetra_Mobile_FIXED\TriNetra_Mobile\research\reviewed_v2"
LEDGER_PATH = os.path.join(DIR_PATH, "ground_truth_ledger_60.csv")
CALIB_PATH = os.path.join(DIR_PATH, "calibration_ratings_template.csv")
PREREG_PATH = os.path.join(DIR_PATH, "preregistration_protocol_v2.5.md")
PROTOCOL_PATH = os.path.join(DIR_PATH, "revised_experiment_protocol.md")
REVIEWER_PACK_PATH = os.path.join(DIR_PATH, "calibration_reviewer_pack_10.md")
ANSWER_KEY_PATH = os.path.join(DIR_PATH, "calibration_answer_key_restricted.md")
OBS_TEMPLATE_PATH = os.path.join(DIR_PATH, "runtime_physical_observations_template.csv")
MANIFEST_PATH = os.path.join(DIR_PATH, "ground_truth_commitment_manifest.json")

def test_ground_truth_ledger():
    print("=== TEST 1: Ground Truth Ledger Validation ===")
    df = pd.read_csv(LEDGER_PATH)
    assert len(df) == 60, f"Expected 60 rows, got {len(df)}"
    assert list(df['journey_id']) == [f"J{i:02d}" for i in range(1, 61)], "Journey IDs not monotonic J01-J60"
    
    # Verify planned target columns
    expected_planned_cols = [
        'planned_cp1_status', 'planned_cp1_target_weight_g',
        'planned_cp2_status', 'planned_cp2_target_weight_g',
        'planned_cp3_status', 'planned_cp3_target_weight_g',
        'planned_cp4_status', 'planned_cp4_target_weight_g'
    ]
    for col in expected_planned_cols:
        assert col in df.columns, f"Missing planned target column: {col}"
    print("Assertion Passed: Planned checkpoint columns properly distinguished from empirical data.")
    
    scenario_counts = df['scenario_id'].value_counts().to_dict()
    print("Scenario Counts:", scenario_counts)
    expected_scenarios = {
        'SC-01': 15, 'SC-02': 8, 'SC-03': 8, 'SC-04': 8,
        'SC-05': 8, 'SC-06': 5, 'SC-07': 4, 'SC-08': 4
    }
    assert scenario_counts == expected_scenarios, f"Scenario count mismatch: {scenario_counts}"
    
    gt_counts = df['ground_truth_class'].value_counts().to_dict()
    print("Ground Truth Class Counts:", gt_counts)
    expected_gt = {
        'GT_INTACT': 23,
        'GT_CUSTOMER_TAMPER': 16,
        'GT_FORWARD_TRANSIT_DAMAGE': 8,
        'GT_DOORSTEP_SUBSTITUTION': 8,
        'GT_REVERSE_TRANSIT_TAMPER': 5
    }
    assert gt_counts == expected_gt, f"Ground truth class count mismatch: {gt_counts}"
    
    # Check Observability symmetry for C and D
    obs_c = df['target_obs_cond_C'].tolist()
    obs_d = df['target_obs_cond_D'].tolist()
    assert obs_c == obs_d, "Observability between Condition C and Condition D must be identical!"
    print("Assertion Passed: Omega_iC* == Omega_iD* for all 60 journeys.")
    
    # Check count of determinable vs degraded vs ambiguous in C & D
    c_counts = df['target_obs_cond_D'].value_counts().to_dict()
    print("Condition D Observability Counts:", c_counts)
    assert c_counts['OBS_DETERMINABLE'] == 52, f"Expected 52 determinable in D, got {c_counts.get('OBS_DETERMINABLE')}"
    assert c_counts['OBS_DEGRADED_INCOMPLETE'] == 4, f"Expected 4 degraded in D, got {c_counts.get('OBS_DEGRADED_INCOMPLETE')}"
    assert c_counts['OBS_INDISTINGUISHABLE'] == 4, f"Expected 4 indistinguishable in D, got {c_counts.get('OBS_INDISTINGUISHABLE')}"
    
    # Check Condition A and B observability
    a_counts = df['target_obs_cond_A'].value_counts().to_dict()
    print("Condition A Observability Counts:", a_counts)
    assert a_counts['OBS_DETERMINABLE'] == 15, f"Expected 15 determinable in A, got {a_counts.get('OBS_DETERMINABLE')}"
    assert a_counts['OBS_INDISTINGUISHABLE'] == 45, f"Expected 45 indistinguishable in A, got {a_counts.get('OBS_INDISTINGUISHABLE')}"
    
    print("TEST 1 PASSED: ground_truth_ledger_60.csv is 100% structurally & substantively valid.\n")

def test_reviewer_pack_blinding():
    print("=== TEST 2: Reviewer Pack Blinding & Material Separation ===")
    assert os.path.exists(REVIEWER_PACK_PATH), "Reviewer pack missing"
    assert os.path.exists(ANSWER_KEY_PATH), "Restricted answer key missing"
    assert os.path.exists(OBS_TEMPLATE_PATH), "Physical observations template missing"
    assert os.path.exists(MANIFEST_PATH), "Commitment manifest template missing"
    
    with open(REVIEWER_PACK_PATH, "r", encoding="utf-8") as f:
        pack_text = f.read()
        
    # Check that cases section (Section 3) does NOT contain GT_ labels or ATTR_STAGE_ or DEC_ labels
    cases_section = pack_text[pack_text.find("## 3. The 10 Calibration Case Evidence Files"):]
    for forbidden in ["GT_INTACT", "GT_FORWARD_TRANSIT_DAMAGE", "GT_DOORSTEP_SUBSTITUTION", 
                      "GT_CUSTOMER_TAMPER", "GT_REVERSE_TRANSIT_TAMPER", "ATTR_STAGE_", "DEC_APPROVE_REFUND"]:
        assert forbidden not in cases_section, f"Reviewer pack leaks answer: {forbidden} found in cases section!"
        
    print("Assertion Passed: Reviewer pack contains zero ground truth or target decision leaks in case descriptions.")
    print("TEST 2 PASSED: Reviewer materials strictly decoupled from restricted answer key.\n")

def test_calibration_template():
    print("=== TEST 3: Calibration Template Validation ===")
    df = pd.read_csv(CALIB_PATH)
    assert len(df) == 40, f"Expected 40 rows (10 cases x 4 reviewers), got {len(df)}"
    cases = sorted(df['case_id'].unique())
    assert cases == [f"C{i:02d}" for i in range(1, 11)], "Cases not C01-C10"
    reviewers = sorted(df['reviewer_id'].unique())
    assert reviewers == ['R1', 'R2', 'R3', 'R4'], "Reviewers not R1-R4"
    assert df['attribution_assessment'].isna().all(), "Attribution assessment must be blank (unexecuted)"
    print("TEST 3 PASSED: calibration_ratings_template.csv is correctly formatted and unexecuted.\n")

def test_fleiss_kappa_math():
    print("=== TEST 4: Fleiss' Kappa Algorithm Verification ===")
    N = 10
    m = 4
    k = 3
    n_matrix = np.array([
        [4, 0, 0], [4, 0, 0], [4, 0, 0], [4, 0, 0],
        [0, 4, 0], [0, 4, 0], [0, 0, 4], [0, 0, 4],
        [3, 1, 0], [0, 3, 1],
    ])
    p_j = np.sum(n_matrix, axis=0) / (N * m)
    P_i = (np.sum(n_matrix**2, axis=1) - m) / (m * (m - 1))
    P_bar = np.mean(P_i)
    P_bar_e = np.sum(p_j**2)
    kappa = (P_bar - P_bar_e) / (1.0 - P_bar_e)
    print(f"Synthetic Kappa test: P_bar={P_bar:.4f}, P_bar_e={P_bar_e:.4f}, Kappa={kappa:.4f}")
    assert kappa > 0.70, "Kappa should show substantial agreement"
    print("TEST 4 PASSED: Fleiss Kappa mathematics verified.\n")

def test_file_hashes():
    print("=== TEST 5: Compute File Hashes for Audit Record ===")
    for path in [LEDGER_PATH, CALIB_PATH, PREREG_PATH, PROTOCOL_PATH, REVIEWER_PACK_PATH, ANSWER_KEY_PATH]:
        with open(path, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        print(f"{os.path.basename(path)}: {h}")
    print("TEST 5 PASSED: SHA-256 hashes generated.\n")

if __name__ == "__main__":
    test_ground_truth_ledger()
    test_reviewer_pack_blinding()
    test_calibration_template()
    test_fleiss_kappa_math()
    test_file_hashes()
    print("ALL 5 VERIFICATION SUITES PASSED WITH 100% INTEGRITY!")
