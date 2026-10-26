#!/usr/bin/env python3
"""
Test: Target Leakage Detection Guard (Remediation C-12, Audit Finding F-04 & F-05).

Verifies that:
1. Target leakage between input attributes/text and evaluation ground-truth labels is detected.
2. If an input column or shallow feature model predicts ground truth with F1 > 0.95,
   the evaluation pipeline flags deterministic target leakage.
3. Detects the circular target leakage in Phase 1 (audit Finding F-04, where complaint_type
   deterministically mapped to conflict_type with F1 = 1.0000).
"""

import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score
from sklearn.preprocessing import OneHotEncoder
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def measure_feature_to_label_leakage(df: pd.DataFrame, feature_col: str, label_col: str) -> float:
    """
    Measures whether a given feature column deterministically predicts the label column.
    Uses one-hot encoding for categorical/text features and a decision tree.
    Returns weighted F1 score.
    """
    X_raw = df[[feature_col]].fillna("MISSING").astype(str)
    encoder = OneHotEncoder(handle_unknown="ignore")
    X = encoder.fit_transform(X_raw)
    y = df[label_col].fillna("NO_CONFLICT").astype(str)

    clf = DecisionTreeClassifier(random_state=42)
    clf.fit(X, y)
    preds = clf.predict(X)
    return float(f1_score(y, preds, average="weighted"))


def test_phase1_target_leakage_detected():
    """
    Finding F-04 verification: In Phase 1 real_complaint_labels.csv,
    'complaint_type' was deterministically mapped to 'conflict_type'
    (COMPLAINT_TO_CONFLICT in build_real_dataset.py).
    Assert that the leakage guard detects F1 > 0.95 (actual 1.0000).
    """
    path = os.path.join(REPO_ROOT, "legacy", "phase-1", "data", "real_complaint_labels.csv")
    assert os.path.exists(path), f"File not found: {path}"

    df = pd.read_csv(path)
    leakage_score = measure_feature_to_label_leakage(df, "complaint_type", "conflict_type")
    print(f"\n[LEAKAGE CHECK] Phase 1 complaint_type -> conflict_type F1: {leakage_score:.4f}")

    assert leakage_score > 0.95, (
        f"Expected target leakage (F1 > 0.95) between complaint_type and conflict_type, got {leakage_score:.4f}"
    )
    print(" -> Leakage guard correctly detected Phase 1 deterministic target leakage (Finding F-04).")


def test_leakage_guard_validator():
    """
    Test the intake guard validator that protects future benchmark datasets from target leakage.
    Must raise ValueError when F1 exceeds 0.95 threshold.
    """
    def assert_no_target_leakage(df: pd.DataFrame, feature_col: str, label_col: str, max_f1: float = 0.95):
        score = measure_feature_to_label_leakage(df, feature_col, label_col)
        if score > max_f1:
            raise ValueError(
                f"LEAKAGE GUARD VIOLATION: Feature '{feature_col}' predicts target '{label_col}' "
                f"with F1={score:.4f} > {max_f1}. Evaluation data is contaminated by target leakage."
            )
        return score

    path = os.path.join(REPO_ROOT, "legacy", "phase-1", "data", "real_complaint_labels.csv")
    df = pd.read_csv(path)

    # Quarantined leaky dataset must be rejected by validator
    with pytest.raises(ValueError, match="LEAKAGE GUARD VIOLATION"):
        assert_no_target_leakage(df, "complaint_type", "conflict_type")

    print("[PASS] test_leakage_guard_validator: Target leakage validator successfully blocks contaminated datasets.")


if __name__ == "__main__":
    test_phase1_target_leakage_detected()
    test_leakage_guard_validator()
    print("\nAll leakage guard tests passed.")
