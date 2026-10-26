# ⚠️ QUARANTINE NOTICE

**Status:** SYNTHETIC — NOT REAL-WORLD DATA  
**Audit reference:** [`audit/label_and_leakage_findings.md`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/audit/label_and_leakage_findings.md)  
**Date quarantined:** 2026-10-23

## What this directory contains

- `customer_complaints_dataset.csv` (271 rows): Copy of template-generated complaints used by `validate_against_real_data.py`.

## Why it is quarantined

This is a copy of the same synthetic dataset from the main `datasets/` directory. The validation script (`validate_against_real_data.py`) hardcoded buyer return rates and seller dispute rates from severity strings, fabricating correlations (Finding F-06).

## Permitted use

- As explicitly labeled synthetic test fixtures
- For code debugging only

## Prohibited use

- As evidence of real-world validity or validated risk scoring
