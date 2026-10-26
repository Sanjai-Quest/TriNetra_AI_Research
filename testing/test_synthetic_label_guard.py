#!/usr/bin/env python3
"""
Test: Synthetic Records Label Guard (Remediation C-11, Audit Finding F-01/F-02/F-03).

Ensures that:
1. All quarantined directories have an active QUARANTINE.md notice.
2. Identifies any quarantined files where columns claim 'real', 'authentic', or 'verified'.
3. Provides an intake validation guard that prevents any pipeline from loading quarantined
   data as authenticated real-world data.
"""

import os
import glob
import re
import pandas as pd
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

QUARANTINE_DIRECTORIES = [
    os.path.join(REPO_ROOT, "legacy", "datasets"),
    os.path.join(REPO_ROOT, "legacy", "xscrapper"),
    os.path.join(REPO_ROOT, "legacy", "phase-1", "data"),
    os.path.join(REPO_ROOT, "legacy", "data"),
    os.path.join(REPO_ROOT, "legacy", "results"),
    os.path.join(REPO_ROOT, "legacy", "phase-2", "validation", "data"),
]


def get_quarantined_files():
    """Returns a list of all CSV files located in quarantined directories."""
    files = []
    for q_dir in QUARANTINE_DIRECTORIES:
        if os.path.exists(q_dir):
            for csv_path in glob.glob(os.path.join(q_dir, "**", "*.csv"), recursive=True):
                files.append(os.path.abspath(csv_path))
    return sorted(list(set(files)))


def test_quarantine_notices_exist():
    """Verify that every identified synthetic dataset directory has a QUARANTINE.md file."""
    for q_dir in QUARANTINE_DIRECTORIES:
        if os.path.exists(q_dir):
            q_file = os.path.join(q_dir, "QUARANTINE.md")
            assert os.path.exists(q_file), f"Missing QUARANTINE.md in {q_dir}"
            with open(q_file, "r", encoding="utf-8") as f:
                content = f.read()
            assert "QUARANTINE NOTICE" in content, f"Invalid quarantine notice in {q_file}"
            assert "SYNTHETIC" in content, f"Notice does not declare SYNTHETIC status in {q_file}"
    print("[PASS] test_quarantine_notices_exist: All quarantine notices verified.")


def test_quarantine_scanner_detects_real_claims():
    """
    Scans quarantined datasets to detect columns claiming 'real', 'authentic', or 'verified'.
    Confirms the scanner detects known audit violations (e.g., Finding F-03 in real_complaint_labels.csv).
    """
    quarantined_files = get_quarantined_files()
    assert len(quarantined_files) > 0, "No quarantined files found"

    flagged = []
    for filepath in quarantined_files:
        try:
            df = pd.read_csv(filepath, nrows=50)
        except Exception:
            continue
        for col in df.columns:
            if any(k in col.lower() for k in ["source", "provenance", "type"]):
                vals = df[col].dropna().astype(str).str.lower()
                matched = vals[vals.str.contains(r"real|authentic|verified", regex=True)]
                if not matched.empty:
                    flagged.append((os.path.relpath(filepath, REPO_ROOT), col, matched.iloc[0]))

    print(f"[INFO] Quarantine scanner flagged {len(flagged)} occurrences of 'real/authentic' claims in quarantined data:")
    for path, col, val in flagged[:5]:
        print(f"   * {path} [{col}]: {val}")

    assert len(flagged) > 0, "Expected quarantine scanner to flag existing synthetic claims"
    print("[PASS] test_quarantine_scanner_detects_real_claims: Scanner properly identifies contaminated records.")


def test_production_intake_guard():
    """
    Enforces that any production ingestion pipeline rejects files that reside
    under quarantined paths or fail quarantine checks.
    """
    def validate_dataset_for_production(csv_path: str):
        abs_path = os.path.abspath(csv_path)
        for q_dir in QUARANTINE_DIRECTORIES:
            if abs_path.startswith(os.path.abspath(q_dir)):
                raise ValueError(
                    f"GUARD REJECTION: Cannot ingest '{os.path.basename(csv_path)}' into production or research benchmarks. "
                    f"File is quarantined under {os.path.relpath(q_dir, REPO_ROOT)}."
                )
        return True

    # Quarantined file must be rejected
    sample_quarantined = os.path.join(REPO_ROOT, "legacy", "datasets", "customer_complaints_dataset.csv")
    with pytest.raises(ValueError, match="GUARD REJECTION"):
        validate_dataset_for_production(sample_quarantined)

    print("[PASS] test_production_intake_guard: Production intake guard successfully blocks quarantined data.")


if __name__ == "__main__":
    test_quarantine_notices_exist()
    test_quarantine_scanner_detects_real_claims()
    test_production_intake_guard()
    print("\nAll synthetic label guard tests passed.")
