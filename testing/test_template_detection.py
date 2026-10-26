#!/usr/bin/env python3
"""
Test: Duplicate & Template Generation Detection Guard (Remediation C-13, Audit Finding F-01 & F-02).

Ensures that:
1. Datasets claiming to be authentic or non-synthetic are screened for template patterns.
2. Any dataset where pairs of records share > 80% token overlap (after stripping stopwords
   and numbers) is flagged as template-generated.
3. Automatically flags `customer_complaints_dataset.csv` and `trinetra_real_complaints_expanded.csv`.
"""

import os
import re
import pandas as pd
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "up", "about", "into", "over", "after", "is", "am",
    "are", "was", "were", "be", "been", "being", "have", "has", "had", "do",
    "does", "did", "this", "that", "these", "those", "i", "you", "he", "she",
    "it", "we", "they", "my", "your", "his", "her", "its", "our", "their"
}


def tokenize_clean(text: str) -> set:
    """Extracts non-numeric, non-stopword tokens of length >= 3."""
    words = re.findall(r"[a-zA-Z]{3,}", str(text).lower())
    return set(w for w in words if w not in STOPWORDS)


def find_high_overlap_pairs(texts: pd.Series, threshold: float = 0.80, max_comparisons: int = 500) -> list:
    """
    Scans for pairs of text entries that share > threshold Jaccard token overlap.
    Returns list of (index_i, index_j, similarity, text_i, text_j).
    """
    token_sets = [tokenize_clean(t) for t in texts]
    high_overlap = []
    n = len(token_sets)

    comparisons = 0
    for i in range(n):
        if not token_sets[i]:
            continue
        # Scan window of adjacent and sampled records
        for j in range(i + 1, min(i + 30, n)):
            if not token_sets[j]:
                continue
            union_len = len(token_sets[i].union(token_sets[j]))
            if union_len == 0:
                continue
            sim = len(token_sets[i].intersection(token_sets[j])) / union_len
            if sim >= threshold:
                high_overlap.append((i, j, sim, str(texts.iloc[i]), str(texts.iloc[j])))
            comparisons += 1
            if comparisons >= max_comparisons and high_overlap:
                break
        if comparisons >= max_comparisons and high_overlap:
            break

    return high_overlap


def test_customer_complaints_flagged_for_template_generation():
    """Confirms template overlap detection on customer_complaints_dataset.csv."""
    path = os.path.join(REPO_ROOT, "legacy", "datasets", "customer_complaints_dataset.csv")
    assert os.path.exists(path), f"File not found: {path}"

    df = pd.read_csv(path)
    pairs = find_high_overlap_pairs(df["Complaint_Text"], threshold=0.80)
    print(f"\n[TEMPLATE CHECK] customer_complaints_dataset.csv: found {len(pairs)} template pairs sharing >= 80% token overlap.")
    for idx_a, idx_b, sim, text_a, text_b in pairs[:2]:
        print(f"  - [{idx_a}] {text_a[:70]}...")
        print(f"    [{idx_b}] {text_b[:70]}... (overlap={sim:.2%})")

    assert len(pairs) > 0, "Expected template detection to flag customer_complaints_dataset.csv"
    print(" -> Successfully flagged customer_complaints_dataset.csv as template-generated.")


def test_expanded_complaints_flagged_for_template_generation():
    """Confirms template overlap detection on trinetra_real_complaints_expanded.csv."""
    path = os.path.join(REPO_ROOT, "legacy", "datasets", "trinetra_real_complaints_expanded.csv")
    assert os.path.exists(path), f"File not found: {path}"

    df = pd.read_csv(path)
    # The expanded dataset uses Complaint_Text column
    text_col = "Complaint_Text" if "Complaint_Text" in df.columns else df.columns[1]
    pairs = find_high_overlap_pairs(df[text_col], threshold=0.80)
    print(f"\n[TEMPLATE CHECK] trinetra_real_complaints_expanded.csv: found {len(pairs)} template pairs sharing >= 80% token overlap.")

    assert len(pairs) > 0, "Expected template detection to flag trinetra_real_complaints_expanded.csv"
    print(" -> Successfully flagged trinetra_real_complaints_expanded.csv as template-generated.")


def test_template_guard_validator():
    """
    Intake guard: Rejects any dataset presented as empirical/real data
    if template overlap exceeds threshold.
    """
    def assert_not_template_generated(df: pd.DataFrame, text_col: str, threshold: float = 0.80):
        pairs = find_high_overlap_pairs(df[text_col], threshold=threshold)
        if pairs:
            raise ValueError(
                f"TEMPLATE GUARD VIOLATION: Detected {len(pairs)} pairs sharing >= {threshold:.0%} "
                f"token overlap in column '{text_col}'. Dataset appears to be template-generated."
            )
        return True

    df = pd.read_csv(os.path.join(REPO_ROOT, "legacy", "datasets", "customer_complaints_dataset.csv"))
    with pytest.raises(ValueError, match="TEMPLATE GUARD VIOLATION"):
        assert_not_template_generated(df, "Complaint_Text")

    print("[PASS] test_template_guard_validator: Template guard correctly blocks template-generated datasets.")


if __name__ == "__main__":
    test_customer_complaints_flagged_for_template_generation()
    test_expanded_complaints_flagged_for_template_generation()
    test_template_guard_validator()
    print("\nAll template detection tests passed.")
