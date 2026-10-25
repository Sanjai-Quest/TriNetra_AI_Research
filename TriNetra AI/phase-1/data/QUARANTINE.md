# ⚠️ QUARANTINE NOTICE

**Status:** SYNTHETIC — NOT REAL-WORLD DATA  
**Audit reference:** [`audit/label_and_leakage_findings.md`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/audit/label_and_leakage_findings.md)  
**Date quarantined:** 2026-10-23

## What this directory contains

- `real_complaint_cases.json` (271 entries): Physical evidence packets fabricated by `build_real_dataset.py` using circular telemetry injection (Finding F-04).
- `synthetic_evidence.csv` (271 rows): Same fabricated evidence in CSV form.
- `ground_truth.csv` / `predictions.csv` (1,000 rows): Pure synthetic benchmark with rigged single-dimension baselines (Finding F-05).

## Why it is quarantined

`build_real_dataset.py` mapped complaint categories to physical anomalies (75% weight drops, SKU character mutations, timestamp inversions) creating guaranteed detection — pure target leakage. The ground truth was derived from the detector's own rules.

## Permitted use

- As explicitly labeled synthetic test fixtures
- For code debugging only

## Prohibited use

- As evidence of real-world validity or physical measurement capability
- As ground truth for research evaluation
- As training data without disclosure
