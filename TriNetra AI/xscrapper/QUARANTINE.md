# ⚠️ QUARANTINE NOTICE

**Status:** SYNTHETIC — NOT REAL-WORLD DATA  
**Audit reference:** [`audit/label_and_leakage_findings.md`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/audit/label_and_leakage_findings.md)  
**Date quarantined:** 2026-10-23

## What this directory contains

- `trinetra_real_complaints_expanded.csv` (1,050 rows): Copy of the expanded synthetic complaint corpus.
- Complaint mining scripts (`build_trinetra_1000_corpus.py`, `expand_master_dataset.py`, `authentic_collector.py`) that generate template-based records.

## Why it is quarantined

The complaint mining pipeline produced synthetic records using hardcoded string templates and fabricated URLs (Findings F-01, F-02). The `authentic_collector.py` name is misleading — it does not collect from live platforms. All output CSVs in this tree are template-generated.

## Permitted use

- As explicitly labeled synthetic test fixtures
- For code debugging only

## Prohibited use

- As evidence of real-world validity
- As ground truth for research evaluation
- As training data without disclosure
