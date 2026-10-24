"""
TriNetra AI: Gate E-3 Reviewer Calibration Fleiss' Kappa Calculation Script
Protocol Version: 2.5.0

Reads empirical reviewer ratings from CSV, constructs contingency matrices,
and computes Fleiss' Kappa for inter-rater agreement on 10 benchmark cases across 4 raters.
"""

import sys
import os
import numpy as np
import pandas as pd

ALLOWED_ATTRIBUTIONS = [
    "ATTR_CONFIRMED_LEGITIMATE",
    "ATTR_STAGE_FORWARD_TRANSIT",
    "ATTR_STAGE_DOORSTEP_DELIVERY",
    "ATTR_STAGE_CONSUMER_CUSTODY",
    "ATTR_STAGE_REVERSE_TRANSIT",
    "ATTR_STAGE_OTHER_OUTSIDE_SCOPE",
    "ATTR_ABSTAIN_INDISTINGUISHABLE",
    "ATTR_ABSTAIN_DEGRADED",
]

ALLOWED_DECISIONS = [
    "DEC_APPROVE_REFUND",
    "DEC_REJECT_REFUND",
    "DEC_HOLD_INVESTIGATION",
    "DEC_CHARGEBACK_CARRIER",
    "DEC_CHARGEBACK_VENDOR",
]

def compute_fleiss_kappa(ratings_df, target_column, allowed_categories):
    """
    Computes Fleiss' Kappa for m raters classifying N cases into k categories.
    
    Parameters:
        ratings_df: DataFrame with columns ['case_id', 'reviewer_id', target_column]
        target_column: Column name to evaluate ('attribution_assessment' or 'operational_decision')
        allowed_categories: List of valid category labels
        
    Returns:
        dict containing:
            - kappa: Fleiss' Kappa value
            - P_bar: Mean observed agreement
            - P_bar_e: Expected agreement by chance
            - contingency_matrix: DataFrame of shape (N, k) with rater counts
            - valid: Boolean whether computation succeeded
    """
    cases = sorted(ratings_df['case_id'].unique())
    reviewers = sorted(ratings_df['reviewer_id'].unique())
    N = len(cases)
    m = len(reviewers)
    k = len(allowed_categories)
    
    # Build contingency matrix: n[i, j] = number of raters who assigned case i to category j
    cat_to_idx = {cat: idx for idx, cat in enumerate(allowed_categories)}
    n_matrix = np.zeros((N, k), dtype=int)
    
    for row_idx, case in enumerate(cases):
        case_rows = ratings_df[ratings_df['case_id'] == case]
        for _, r in case_rows.iterrows():
            val = str(r[target_column]).strip()
            if val not in cat_to_idx:
                raise ValueError(f"Invalid category value '{val}' for case {case}, reviewer {r['reviewer_id']}. Must be one of {allowed_categories}")
            col_idx = cat_to_idx[val]
            n_matrix[row_idx, col_idx] += 1
            
    # Verify each case has exactly m ratings
    row_sums = np.sum(n_matrix, axis=1)
    if not np.all(row_sums == m):
        raise ValueError(f"Incomplete ratings: expected exactly {m} ratings per case, found {row_sums}")
        
    # p_j: Proportion of all assignments to category j
    p_j = np.sum(n_matrix, axis=0) / (N * m)
    
    # P_i: Extent to which raters agree for the i-th subject
    P_i = (np.sum(n_matrix**2, axis=1) - m) / (m * (m - 1))
    
    # P_bar: Mean observed agreement
    P_bar = np.mean(P_i)
    
    # P_bar_e: Expected agreement by chance
    P_bar_e = np.sum(p_j**2)
    
    # Fleiss' Kappa
    if P_bar_e == 1.0:
        kappa = 1.0
    else:
        kappa = (P_bar - P_bar_e) / (1.0 - P_bar_e)
        
    contingency_df = pd.DataFrame(n_matrix, index=cases, columns=allowed_categories)
    
    return {
        "kappa": float(kappa),
        "P_bar": float(P_bar),
        "P_bar_e": float(P_bar_e),
        "N": N,
        "m": m,
        "k": k,
        "contingency_matrix": contingency_df,
    }

def evaluate_calibration_ratings(csv_path):
    """
    Validates completed calibration ratings CSV and computes Fleiss' Kappa for both
    attribution assessment and operational decision.
    """
    if not os.path.exists(csv_path):
        print(f"ERROR: File not found: {csv_path}")
        return False
        
    df = pd.read_csv(csv_path)
    required_cols = ['case_id', 'reviewer_id', 'attribution_assessment', 'operational_decision']
    for col in required_cols:
        if col not in df.columns:
            print(f"ERROR: Missing required column '{col}' in {csv_path}")
            return False
            
    # Check if empty / unexecuted
    if df['attribution_assessment'].isna().all():
        print(f"STATUS: Ratings template at {csv_path} is UNEXECUTED (all attribution assessments are blank).")
        print("Gate E-3 remains PENDING until four real reviewers submit their ratings.")
        return False
        
    # Check for partial completion
    null_count = df['attribution_assessment'].isna().sum()
    if null_count > 0:
        print(f"STATUS: Incomplete ratings: {null_count} / {len(df)} entries are blank. Complete all 40 ratings before computing Kappa.")
        return False
        
    print(f"--- Computing Fleiss' Kappa from {len(df)} empirical ratings ---")
    
    # 1. Primary: Attribution Assessment
    attr_results = compute_fleiss_kappa(df, 'attribution_assessment', ALLOWED_ATTRIBUTIONS)
    print("\n1. Attribution Assessment Agreement:")
    print(f"   Observed Agreement (P_bar):    {attr_results['P_bar']:.4f}")
    print(f"   Chance Agreement (P_bar_e):   {attr_results['P_bar_e']:.4f}")
    print(f"   Fleiss' Kappa (κ):             {attr_results['kappa']:.4f}")
    
    # 2. Secondary: Operational Decision
    dec_results = compute_fleiss_kappa(df, 'operational_decision', ALLOWED_DECISIONS)
    print("\n2. Operational Decision Agreement:")
    print(f"   Observed Agreement (P_bar):    {dec_results['P_bar']:.4f}")
    print(f"   Chance Agreement (P_bar_e):   {dec_results['P_bar_e']:.4f}")
    print(f"   Fleiss' Kappa (κ):             {dec_results['kappa']:.4f}")
    
    # Threshold check
    threshold = 0.60
    cleared = attr_results['kappa'] >= threshold
    print("\n--- Gate E-3 Evaluation Verdict ---")
    print(f"Threshold Required: κ >= {threshold:.2f}")
    print(f"Primary Attribution κ: {attr_results['kappa']:.4f}")
    if cleared:
        print("RESULT: Gate E-3 CLEARED (Substantial inter-reviewer agreement achieved).")
    else:
        print(f"RESULT: Gate E-3 NOT CLEARED (κ = {attr_results['kappa']:.4f} < {threshold:.2f}). Additional reviewer alignment required.")
        
    return cleared

def check_individual_forms(dir_path):
    """Checks if individual reviewer response forms (R1-R4) are present and populated."""
    forms = [os.path.join(dir_path, f"calibration_response_form_R{i}.csv") for i in range(1, 5)]
    all_exist = all(os.path.exists(f) for f in forms)
    if not all_exist:
        return None
    dfs = [pd.read_csv(f) for f in forms]
    combined_df = pd.concat(dfs, ignore_index=True)
    if not combined_df['attribution_assessment'].isna().all():
        return combined_df
    return None

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    if len(sys.argv) > 1:
        target_csv = sys.argv[1]
        evaluate_calibration_ratings(target_csv)
    else:
        # Check individual forms first
        indiv_df = check_individual_forms(base_dir)
        if indiv_df is not None and not indiv_df['attribution_assessment'].isna().all():
            temp_path = os.path.join(base_dir, "calibration_ratings_consolidated.csv")
            indiv_df.to_csv(temp_path, index=False)
            evaluate_calibration_ratings(temp_path)
        else:
            target_csv = os.path.join(base_dir, "calibration_ratings_template.csv")
            evaluate_calibration_ratings(target_csv)

