"""
TriNetra AI: Synthetic Reviewer Dry-Run Execution Harness
Protocol Version: 2.5.0 (Synthetic Rehearsal Mode)

Executes four synthetic reviewer profiles (deterministic rule mappings: Profile A, B, C, D)
against 10 diagnostic mock cases (DRYRUN-01 to DRYRUN-10).
Validates schema, checks consistency, and tests agreement calculation.

DISCLAIMER: SYNTHETIC DATA ONLY. NOT GENUINE HUMAN REVIEW DATA.
DOES NOT CLEAR GATE E-3.
"""

import os
import sys
import json
import numpy as np
import pandas as pd

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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

# Synthetic agent decision definitions
def evaluate_agent_a(case_id):
    """Agent A: Evidence-First Reviewer (Strict literal evidence matching)"""
    # Case logic based on positive explicit evidence
    mapping = {
        "DRYRUN-01": (
            "ATTR_CONFIRMED_LEGITIMATE",
            "DEC_APPROVE_REFUND",
            5,
            "Intact tamper seal #H-4412 and matching gross weight (400.0g-400.2g) across all four checkpoints corroborate genuine return."
        ),
        "DRYRUN-02": (
            "ATTR_STAGE_FORWARD_TRANSIT",
            "DEC_CHARGEBACK_CARRIER",
            5,
            "Courier photograph at CP2 delivery and conveyor drop note prove corner crush and fluid leak originated during forward transit."
        ),
        "DRYRUN-03": (
            "ATTR_STAGE_DOORSTEP_DELIVERY",
            "DEC_CHARGEBACK_CARRIER",
            4,
            "Doorstep delivery photo at CP2 confirms plain brown box with handwritten text substituted for branded box before handover."
        ),
        "DRYRUN-04": (
            "ATTR_STAGE_CONSUMER_CUSTODY",
            "DEC_REJECT_REFUND",
            5,
            "Factory shrinkwrap intact at CP2 delivery; sliced and scotch-taped with 240.0g weight deficit at CP3 pickup, isolating dummy swap to consumer custody."
        ),
        "DRYRUN-05": (
            "ATTR_STAGE_REVERSE_TRANSIT",
            "DEC_CHARGEBACK_CARRIER",
            5,
            "Tamper-evident security pouch #SEC-9904 confirmed intact at CP3 (510.0g) and slit open with 195.0g weight loss at CP4, isolating theft to reverse carrier transit."
        ),
        "DRYRUN-06": (
            "ATTR_STAGE_OTHER_OUTSIDE_SCOPE",
            "DEC_CHARGEBACK_VENDOR",
            5,
            "All physical tamper stickers intact across CP1-CP4; laboratory diagnosis confirms internal un-soldered PCB track originating from factory manufacturing."
        ),
        "DRYRUN-07": (
            "ATTR_ABSTAIN_DEGRADED",
            "DEC_HOLD_INVESTIGATION",
            4,
            "CP3 pickup photograph underexposed (<3 lux) and scale failed (0.0g); missing boundary evidence prevents isolating stage of earbud loss."
        ),
        "DRYRUN-08": (
            "ATTR_ABSTAIN_DEGRADED",
            "DEC_HOLD_INVESTIGATION",
            4,
            "Rotational motion blur and disconnected scale (0.0g) at CP2 delivery obscure delivery state, confounding forward transit and customer custody."
        ),
        "DRYRUN-09": (
            "ATTR_ABSTAIN_INDISTINGUISHABLE",
            "DEC_HOLD_INVESTIGATION",
            4,
            "Intense specular flash flare covers the top-right camera corner at both CP2 and CP3, making it impossible to isolate when hairline crack occurred."
        ),
        "DRYRUN-10": (
            "ATTR_CONFIRMED_LEGITIMATE",
            "DEC_APPROVE_REFUND",
            4,
            "Packaging seals remained intact throughout; depot maintenance audit confirms -50.0g scale drift at CP2/CP3 and warehouse confirms intact genuine unit."
        ),
    }
    attr, dec, conf, notes = mapping[case_id]
    return {
        "case_id": case_id,
        "reviewer_id": "AGENT_A",
        "attribution_assessment": attr,
        "operational_decision": dec,
        "confidence_score": conf,
        "justification_notes": notes
    }

def evaluate_agent_b(case_id):
    """Agent B: Alternative-Explanation Reviewer (Multi-hypothesis auditing)"""
    mapping = {
        "DRYRUN-01": (
            "ATTR_CONFIRMED_LEGITIMATE",
            "DEC_APPROVE_REFUND",
            5,
            "No plausible alternative explanation exists; identical weights and pristine seals eliminate tampering or courier theft."
        ),
        "DRYRUN-02": (
            "ATTR_STAGE_FORWARD_TRANSIT",
            "DEC_CHARGEBACK_CARRIER",
            5,
            "Courier log admission and matching corner puncture eliminate pre-shipment defect and customer damage hypotheses."
        ),
        "DRYRUN-03": (
            "ATTR_STAGE_FORWARD_TRANSIT",
            "DEC_CHARGEBACK_CARRIER",
            4,
            "Competing hypotheses exist between forward line-haul transit depot substitution and delivery agent doorstep swap; attribution assigned to forward transit chain."
        ),
        "DRYRUN-04": (
            "ATTR_STAGE_CONSUMER_CUSTODY",
            "DEC_REJECT_REFUND",
            5,
            "Immediate tape swap and ceramic tile substitution at CP3 eliminate carrier theft alternatives, as customer possessed parcel between CP2 and CP3."
        ),
        "DRYRUN-05": (
            "ATTR_STAGE_REVERSE_TRANSIT",
            "DEC_CHARGEBACK_CARRIER",
            5,
            "Pouch barcode and seal verified at CP3 eliminate consumer return fraud; razor breach at CP4 conclusively establishes reverse transit carrier liability."
        ),
        "DRYRUN-06": (
            "ATTR_STAGE_OTHER_OUTSIDE_SCOPE",
            "DEC_CHARGEBACK_VENDOR",
            5,
            "Pristine unbroken seals across all four handovers conclusively falsify transit damage or consumer disassembly hypotheses; vendor defect confirmed."
        ),
        "DRYRUN-07": (
            "ATTR_ABSTAIN_DEGRADED",
            "DEC_HOLD_INVESTIGATION",
            4,
            "Unrecorded CP3 state leaves both consumer custody theft and reverse courier theft equally plausible; mandatory abstention under competing hypotheses."
        ),
        "DRYRUN-08": (
            "ATTR_ABSTAIN_DEGRADED",
            "DEC_HOLD_INVESTIGATION",
            4,
            "Severe motion blur leaves forward carrier substitution and customer tampering indistinguishable; abstention required."
        ),
        "DRYRUN-09": (
            "ATTR_ABSTAIN_INDISTINGUISHABLE",
            "DEC_HOLD_INVESTIGATION",
            5,
            "Photographic glare leaves transit impact, courier drop, and customer impact equally plausible alternative explanations."
        ),
        "DRYRUN-10": (
            "ATTR_CONFIRMED_LEGITIMATE",
            "DEC_APPROVE_REFUND",
            4,
            "Alternative explanation of partial theft is falsified by depot scale calibration log confirming systematic -50g instrumentation error."
        ),
    }
    attr, dec, conf, notes = mapping[case_id]
    return {
        "case_id": case_id,
        "reviewer_id": "AGENT_B",
        "attribution_assessment": attr,
        "operational_decision": dec,
        "confidence_score": conf,
        "justification_notes": notes
    }

def evaluate_agent_c(case_id):
    """Agent C: Journey-Stage Reviewer (Longitudinal custody boundary tracking)"""
    mapping = {
        "DRYRUN-01": (
            "ATTR_CONFIRMED_LEGITIMATE",
            "DEC_APPROVE_REFUND",
            5,
            "Longitudinal mass and seal telemetry invariant across Boundary 1 (CP1-CP2), Boundary 2 (CP2-CP3), and Boundary 3 (CP3-CP4)."
        ),
        "DRYRUN-02": (
            "ATTR_STAGE_FORWARD_TRANSIT",
            "DEC_CHARGEBACK_CARRIER",
            5,
            "State transition Delta S occurs strictly across Boundary 1 (CP1 to CP2); downstream states at CP3 and CP4 remain invariant."
        ),
        "DRYRUN-03": (
            "ATTR_STAGE_DOORSTEP_DELIVERY",
            "DEC_CHARGEBACK_CARRIER",
            4,
            "State transition documented at CP2 delivery boundary where unbranded packaging was presented and rejected; isolated to forward delivery handover."
        ),
        "DRYRUN-04": (
            "ATTR_STAGE_CONSUMER_CUSTODY",
            "DEC_REJECT_REFUND",
            5,
            "State transition Delta S (seal sliced, weight -240.0g) occurs strictly across Boundary 2 (between CP2 delivery acceptance and CP3 return pickup)."
        ),
        "DRYRUN-05": (
            "ATTR_STAGE_REVERSE_TRANSIT",
            "DEC_CHARGEBACK_CARRIER",
            5,
            "State transition Delta S (pouch slit, weight -195.0g) occurs strictly across Boundary 3 (between CP3 pickup and CP4 intake)."
        ),
        "DRYRUN-06": (
            "ATTR_STAGE_OTHER_OUTSIDE_SCOPE",
            "DEC_CHARGEBACK_VENDOR",
            5,
            "Zero state transitions observed across Boundaries 1, 2, or 3; defect localized upstream prior to CP1 seller dispatch."
        ),
        "DRYRUN-07": (
            "ATTR_ABSTAIN_DEGRADED",
            "DEC_HOLD_INVESTIGATION",
            4,
            "Boundary 2 and Boundary 3 state vectors unidentifiable due to sensor failure at intermediate node CP3."
        ),
        "DRYRUN-08": (
            "ATTR_ABSTAIN_DEGRADED",
            "DEC_HOLD_INVESTIGATION",
            4,
            "Boundary 1 (CP1-CP2) and Boundary 2 (CP2-CP3) confounded by unreadable node CP2; longitudinal isolation fails."
        ),
        "DRYRUN-09": (
            "ATTR_ABSTAIN_INDISTINGUISHABLE",
            "DEC_HOLD_INVESTIGATION",
            4,
            "State delta detected only at CP4; intermediate boundary states at CP2 and CP3 are occluded by glare, preventing localization."
        ),
        "DRYRUN-10": (
            "ATTR_CONFIRMED_LEGITIMATE",
            "DEC_APPROVE_REFUND",
            4,
            "Apparent mass delta at CP2/CP3 resolved as node sensor offset; true package state invariant across all boundaries."
        ),
    }
    attr, dec, conf, notes = mapping[case_id]
    return {
        "case_id": case_id,
        "reviewer_id": "AGENT_C",
        "attribution_assessment": attr,
        "operational_decision": dec,
        "confidence_score": conf,
        "justification_notes": notes
    }

def evaluate_agent_d(case_id):
    """Agent D: Uncertainty and Abstention Reviewer (Noise filtering and abstention safeguard)"""
    mapping = {
        "DRYRUN-01": (
            "ATTR_CONFIRMED_LEGITIMATE",
            "DEC_APPROVE_REFUND",
            5,
            "High SNR across all optical captures and calibrated balance readings; zero sensor degradation; return verified legitimate."
        ),
        "DRYRUN-02": (
            "ATTR_STAGE_FORWARD_TRANSIT",
            "DEC_CHARGEBACK_CARRIER",
            5,
            "Unambiguous physical impact documentation and courier incident log provide clear signal for forward transit damage."
        ),
        "DRYRUN-03": (
            "ATTR_STAGE_DOORSTEP_DELIVERY",
            "DEC_CHARGEBACK_CARRIER",
            4,
            "Delivery photo provides clear optical proof of package substitution; customer rejection recorded on spot."
        ),
        "DRYRUN-04": (
            "ATTR_STAGE_CONSUMER_CUSTODY",
            "DEC_REJECT_REFUND",
            5,
            "Clear photographic evidence of scotch tape over factory seal and -240.0g deficit confirms consumer custody tampering."
        ),
        "DRYRUN-05": (
            "ATTR_STAGE_REVERSE_TRANSIT",
            "DEC_CHARGEBACK_CARRIER",
            5,
            "Clear barcode and seal scan at CP3 contrasted with razor slit at CP4 provides high-certainty proof of reverse transit breach."
        ),
        "DRYRUN-06": (
            "ATTR_STAGE_OTHER_OUTSIDE_SCOPE",
            "DEC_CHARGEBACK_VENDOR",
            5,
            "Clear diagnostic confirmation of manufacturing solder omission with pristine factory seals."
        ),
        "DRYRUN-07": (
            "ATTR_ABSTAIN_DEGRADED",
            "DEC_HOLD_INVESTIGATION",
            5,
            "Mandatory abstention triggered: CP3 photograph illuminance <3 lux and scale reports 0.0g error."
        ),
        "DRYRUN-08": (
            "ATTR_ABSTAIN_DEGRADED",
            "DEC_HOLD_INVESTIGATION",
            5,
            "Mandatory abstention triggered: severe rotational motion blur at CP2 and scale communication drop (0.0g)."
        ),
        "DRYRUN-09": (
            "ATTR_ABSTAIN_INDISTINGUISHABLE",
            "DEC_HOLD_INVESTIGATION",
            5,
            "Mandatory abstention triggered: specular flash flare conceals defect location across multiple handovers."
        ),
        "DRYRUN-10": (
            "ATTR_ABSTAIN_INDISTINGUISHABLE",
            "DEC_HOLD_INVESTIGATION",
            3,
            "Sensor conflict detected: -50.0g scale anomaly contradicts intact visual packaging; holds investigation pending scale calibration certificate verification."
        ),
    }
    attr, dec, conf, notes = mapping[case_id]
    return {
        "case_id": case_id,
        "reviewer_id": "AGENT_D",
        "attribution_assessment": attr,
        "operational_decision": dec,
        "confidence_score": conf,
        "justification_notes": notes
    }

def compute_fleiss_kappa(ratings_df, target_col, categories):
    cases = sorted(ratings_df['case_id'].unique())
    reviewers = sorted(ratings_df['reviewer_id'].unique())
    N = len(cases)
    m = len(reviewers)
    k = len(categories)
    
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    n_matrix = np.zeros((N, k), dtype=int)
    
    for r_idx, case in enumerate(cases):
        sub = ratings_df[ratings_df['case_id'] == case]
        for _, row in sub.iterrows():
            val = str(row[target_col]).strip()
            if val not in cat_to_idx:
                raise ValueError(f"Invalid category: {val}")
            c_idx = cat_to_idx[val]
            n_matrix[r_idx, c_idx] += 1
            
    p_j = np.sum(n_matrix, axis=0) / (N * m)
    P_i = (np.sum(n_matrix**2, axis=1) - m) / (m * (m - 1))
    P_bar = np.mean(P_i)
    P_bar_e = np.sum(p_j**2)
    kappa = (P_bar - P_bar_e) / (1.0 - P_bar_e) if P_bar_e != 1.0 else 1.0
    
    return {
        "kappa": float(kappa),
        "P_bar": float(P_bar),
        "P_bar_e": float(P_bar_e),
        "contingency_matrix": pd.DataFrame(n_matrix, index=cases, columns=categories)
    }

def main():
    cases = [f"DRYRUN-{i:02d}" for i in range(1, 11)]
    agents = [
        ("AGENT_A", evaluate_agent_a),
        ("AGENT_B", evaluate_agent_b),
        ("AGENT_C", evaluate_agent_c),
        ("AGENT_D", evaluate_agent_d),
    ]
    
    results = []
    print("--- Executing Synthetic Reviewers (Deterministic Rule Mappings) ---")
    for agent_id, eval_fn in agents:
        print(f"Executing {agent_id} across 10 cases...")
        for case in cases:
            res = eval_fn(case)
            # Schema validation
            assert res['case_id'] in cases
            assert res['reviewer_id'] == agent_id
            assert res['attribution_assessment'] in ALLOWED_ATTRIBUTIONS, f"Invalid attr: {res['attribution_assessment']}"
            assert res['operational_decision'] in ALLOWED_DECISIONS, f"Invalid dec: {res['operational_decision']}"
            assert 1 <= res['confidence_score'] <= 5
            assert len(res['justification_notes']) > 10
            results.append(res)
            
    df = pd.DataFrame(results)
    out_csv = os.path.join(os.path.dirname(__file__), "synthetic_agent_results.csv")
    df.to_csv(out_csv, index=False)
    print(f"SUCCESS: Generated {len(df)} synthetic ratings -> {out_csv}")
    
    # Compute Agreement
    attr_res = compute_fleiss_kappa(df, 'attribution_assessment', ALLOWED_ATTRIBUTIONS)
    dec_res = compute_fleiss_kappa(df, 'operational_decision', ALLOWED_DECISIONS)
    
    print("\n--- Synthetic Agreement Results (DIAGNOSTIC ONLY - NOT HUMAN DATA) ---")
    print(f"1. Attribution Assessment Fleiss' Kappa: kappa = {attr_res['kappa']:.4f} (Observed: {attr_res['P_bar']:.4f}, Chance: {attr_res['P_bar_e']:.4f})")
    print(f"2. Operational Decision Fleiss' Kappa:    kappa = {dec_res['kappa']:.4f} (Observed: {dec_res['P_bar']:.4f}, Chance: {dec_res['P_bar_e']:.4f})")
    
    # Check inconsistencies
    print("\n--- Diagnostic Inconsistencies Identified ---")
    for case in cases:
        case_df = df[df['case_id'] == case]
        attrs = case_df['attribution_assessment'].unique()
        decs = case_df['operational_decision'].unique()
        if len(attrs) > 1 or len(decs) > 1:
            print(f"Case {case}: Divergence found!")
            for _, r in case_df.iterrows():
                print(f"   [{r['reviewer_id']}] Attr: {r['attribution_assessment']} | Dec: {r['operational_decision']} | Notes: {r['justification_notes']}")

if __name__ == "__main__":
    main()
