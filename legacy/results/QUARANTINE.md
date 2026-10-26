# ⚠️ QUARANTINE NOTICE

**Status:** SYNTHETIC — NOT REAL-WORLD DATA  
**Audit reference:** [`audit/label_and_leakage_findings.md`](label_and_leakage_findings.md)  
**Date quarantined:** 2026-10-23

## What this directory contains

- `real_complaint_results.json`: Evaluation metrics (F1=1.000, McNemar p=2.7e-16) produced by `evaluate_real_complaints.py`.

## Why it is quarantined

These results were computed from circular synthetic evidence and rigged baselines (Findings F-04, F-05). The statistical significance is scientifically void — the evaluation tested whether the engine detects anomalies it hardcoded into the input seconds earlier.

## Permitted use

- As explicitly labeled synthetic evaluation output
- For code debugging only

## Prohibited use

- As evidence of system accuracy, statistical significance, or research validity
