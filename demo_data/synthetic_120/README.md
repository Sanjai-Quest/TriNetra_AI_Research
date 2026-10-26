# Synthetic Dry Run Demonstration Dataset

> **STATUS: SYNTHETIC DATASET — DRY RUN DEMO ONLY**  
> **DO NOT CITE OR REPORT AS EMPIRICAL PHYSICAL TRIAL RESULTS**

---

## Purpose

This directory (`demo_data/synthetic_120/`) contains programmatically generated demonstration fixtures built strictly for Phase 1 pipeline review, user interface verification, and end-to-end dry-run benchmarking.

## Anti-Fabrication Guarantees

1. **Independent Namespace:** Every journey code is strictly prefixed `SYN-` (e.g., `SYN-2026-0001` through `SYN-2026-0120`) to prevent any possible collision with real physical trial data.
2. **Mandatory Metadata Tag:** Every JSON manifest, database record, and CSV row carries `"synthetic": true`.
3. **Visual Watermarks:** Every rendered box image is stamped with a red `[SYNTHETIC DEMO]` watermark in the corner.
4. **Evaluator Refusal Guard:** The primary research experiment runner (`trinetra eval e1`) automatically inspects inputs and refuses to evaluate datasets from `demo_data/` unless explicitly overridden with `--allow-synthetic-dry-run`.
5. **Report Watermarks:** All tables, LaTeX exports, risk-coverage figures, and provenance manifests generated from this dataset are prominently watermarked:
   `SYNTHETIC DRY RUN — NOT A RESULT`.
