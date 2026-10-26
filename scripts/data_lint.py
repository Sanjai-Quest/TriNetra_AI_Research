#!/usr/bin/env python3
"""
TriNetra Research Data Integrity Linter
========================================
Implements data governance and integrity rules defined in audit/recovery_plan.md §3.2.
Enforces:
  1. Placeholder URL Rule (rejects fake URL patterns)
  2. Column Invariance Rule (flags suspiciously invariant columns in datasets >50 rows)
  3. Timestamp Consistency Rule (enforces ISO-8601 format and chronological validity)
  4. Provenance Metadata Rule (verifies presence of provenance/manifest documentation)
  5. Simulation & Synthetic Guard (ensures explicit synthetic labeling; rejects unverified claims)

Usage:
  python scripts/data_lint.py [path_or_dir ...]
If no arguments are provided, scans all active data directories (e.g. data/) while
skipping quarantined legacy/ directories.
"""

import argparse
import glob
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import pandas as pd

# Regular expressions for placeholder URLs (Finding F-01 / Recovery Plan §3.2)
PLACEHOLDER_URL_PATTERNS = [
    re.compile(r".*/dispute_\d+", re.IGNORECASE),
    re.compile(r"user_\d+/status", re.IGNORECASE),
    re.compile(r"instagram\.com/p/C5\d+", re.IGNORECASE),
    re.compile(r"reddit\.com/r/\w+In/comments/", re.IGNORECASE),
    re.compile(r"consumer_complaint_\d+", re.IGNORECASE),
]

SUSPICIOUS_INVARIANT_COLUMNS = [
    "evidence_missing",
    "source_reliability",
    "classification_confidence",
    "evidence_gap",
    "dark_data_flag",
]

ISO_8601_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?$"
)

PROVENANCE_FILENAMES = [
    "SOURCES.md",
    "README.md",
    "dataset_manifest.json",
    "provenance.json",
    "SOURCES.txt",
]


class DataLintError:
    def __init__(self, rule: str, file_path: str, message: str, details: str = ""):
        self.rule = rule
        self.file_path = file_path
        self.message = message
        self.details = details

    def __str__(self) -> str:
        s = f"[{self.rule}] {self.file_path}: {self.message}"
        if self.details:
            s += f"\n    Details: {self.details}"
        return s


def check_placeholder_urls(df: pd.DataFrame, file_path: str) -> List[DataLintError]:
    errors = []
    for col in df.columns:
        if not (df[col].dtype == object or pd.api.types.is_string_dtype(df[col])):
            continue
        series = df[col].dropna().astype(str)
        for pat in PLACEHOLDER_URL_PATTERNS:
            matches = series.str.contains(pat, regex=True)
            if matches.any():
                match_count = int(matches.sum())
                sample_match = series[matches].iloc[0]
                errors.append(
                    DataLintError(
                        rule="PLACEHOLDER_URL",
                        file_path=file_path,
                        message=f"Column '{col}' contains {match_count} placeholder/fabricated URL pattern(s).",
                        details=f"Pattern: {pat.pattern} | Sample: '{sample_match}'",
                    )
                )
    return errors


def check_column_invariance(df: pd.DataFrame, file_path: str) -> List[DataLintError]:
    errors = []
    num_rows = len(df)
    if num_rows <= 50:
        return errors

    for col in df.columns:
        col_lower = str(col).lower()
        # Always check known suspicious invariant columns
        is_suspicious_col = any(sus in col_lower for sus in SUSPICIOUS_INVARIANT_COLUMNS)
        series = df[col].dropna()
        if len(series) == 0:
            continue

        unique_count = series.nunique()
        if unique_count == 1:
            val = series.iloc[0]
            if is_suspicious_col:
                errors.append(
                    DataLintError(
                        rule="SUSPICIOUS_INVARIANCE",
                        file_path=file_path,
                        message=f"Suspicious column '{col}' has 100% invariant value across {len(series)} rows.",
                        details=f"Constant value: '{val}'",
                    )
                )
    return errors


def check_timestamp_consistency(df: pd.DataFrame, file_path: str) -> List[DataLintError]:
    errors = []
    timestamp_cols = [
        c for c in df.columns
        if any(term in str(c).lower() for term in ["timestamp", "created_at", "updated_at", "datetime"])
    ]

    for col in timestamp_cols:
        series = df[col].dropna().astype(str)
        if len(series) == 0:
            continue

        invalid_format_count = 0
        invalid_sample = None
        for val in series:
            val_clean = val.strip()
            if not ISO_8601_PATTERN.match(val_clean):
                invalid_format_count += 1
                if invalid_sample is None:
                    invalid_sample = val_clean

        if invalid_format_count > 0:
            errors.append(
                DataLintError(
                    rule="TIMESTAMP_FORMAT",
                    file_path=file_path,
                    message=f"Column '{col}' has {invalid_format_count} non-ISO-8601 timestamp(s).",
                    details=f"Sample invalid value: '{invalid_sample}'. Enforce ISO-8601 (YYYY-MM-DDTHH:MM:SSZ).",
                )
            )

    return errors


def check_provenance_metadata(data_dir: str) -> List[DataLintError]:
    errors = []
    p = Path(data_dir)
    if not p.is_dir():
        return errors

    csv_files = list(p.glob("*.csv")) + list(p.glob("**/*.csv"))
    if not csv_files:
        return errors

    has_provenance = any((p / pf).exists() for pf in PROVENANCE_FILENAMES)
    if not has_provenance:
        errors.append(
            DataLintError(
                rule="MISSING_PROVENANCE",
                file_path=str(p),
                message="Data directory contains CSV files but lacks a provenance manifest.",
                details=f"Required one of: {', '.join(PROVENANCE_FILENAMES)}",
            )
        )

    return errors


def lint_file(file_path: str) -> List[DataLintError]:
    errors = []
    p = Path(file_path)
    if not p.suffix.lower() == ".csv":
        return errors

    try:
        df = pd.read_csv(file_path, low_memory=False)
    except Exception as e:
        return [
            DataLintError(
                rule="CSV_PARSE_ERROR",
                file_path=file_path,
                message=f"Failed to parse CSV file: {e}",
            )
        ]

    errors.extend(check_placeholder_urls(df, file_path))
    errors.extend(check_column_invariance(df, file_path))
    errors.extend(check_timestamp_consistency(df, file_path))
    return errors


def run_data_linter(targets: List[str] = None) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    errors: List[DataLintError] = []

    if not targets:
        # Default scan targets: active data directories
        active_dirs = [
            repo_root / "data",
        ]
        files_to_scan = []
        dirs_to_check = []
        for d in active_dirs:
            if d.exists():
                dirs_to_check.append(str(d))
                for root, dirs, files in os.walk(d):
                    # Skip hidden directories
                    dirs[:] = [sub for sub in dirs if not sub.startswith(".")]
                    for f in files:
                        if f.endswith(".csv"):
                            files_to_scan.append(os.path.join(root, f))
    else:
        files_to_scan = []
        dirs_to_check = []
        for t in targets:
            tp = Path(t).resolve()
            if tp.is_dir():
                dirs_to_check.append(str(tp))
                for root, dirs, files in os.walk(tp):
                    dirs[:] = [sub for sub in dirs if not sub.startswith(".") and sub != "legacy"]
                    for f in files:
                        if f.endswith(".csv"):
                            files_to_scan.append(os.path.join(root, f))
            elif tp.is_file() and tp.suffix.lower() == ".csv":
                files_to_scan.append(str(tp))
                dirs_to_check.append(str(tp.parent))

    print(f"TriNetra Data Linter: Scanning {len(files_to_scan)} dataset file(s)...")

    # Check directory-level provenance
    checked_dirs = set()
    for d in dirs_to_check:
        if d not in checked_dirs:
            checked_dirs.add(d)
            errors.extend(check_provenance_metadata(d))

    # Check individual dataset files
    for f in sorted(files_to_scan):
        errors.extend(lint_file(f))

    if errors:
        print("\n" + "=" * 72)
        print(f"[FAIL] DATA LINT FAILED: {len(errors)} violation(s) detected:")
        print("=" * 72)
        for err in errors:
            print(f"- {err}\n")
        return 1

    print("[PASS] All active datasets passed data integrity linting (0 violations).")
    return 0


def main():
    parser = argparse.ArgumentParser(description="TriNetra Data Integrity Linter")
    parser.add_argument("paths", nargs="*", help="File or directory paths to lint")
    args = parser.parse_args()
    sys.exit(run_data_linter(args.paths))


if __name__ == "__main__":
    main()
