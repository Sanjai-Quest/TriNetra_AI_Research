# ⚠️ QUARANTINE NOTICE

**Status:** SYNTHETIC — NOT REAL-WORLD DATA  
**Audit reference:** [`audit/label_and_leakage_findings.md`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/audit/label_and_leakage_findings.md)  
**Date quarantined:** 2026-10-23

## What this directory contains

- `real_complaint_predictions.csv` (271 rows): Evaluation output from running the circular Phase 1 pipeline.

## Why it is quarantined

These predictions were produced by running `ReconciliationEngine` against evidence packets that were fabricated specifically to trigger its detection rules (Finding F-04, F-05). The resulting F1=1.000 and p=2.7e-16 are artifacts of target leakage, not empirical evidence.

## Permitted use

- As explicitly labeled synthetic evaluation output
- For code debugging only

## Prohibited use

- As evidence of system accuracy or research validity
