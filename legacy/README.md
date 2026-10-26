# Legacy Material Quarantine Archive

> **STATUS: QUARANTINED — DO NOT CITE OR REPORT AS EMPIRICAL RESULTS**  
> **BINDING AUDIT NOTICE:** Refer to `audit/label_and_leakage_findings.md`, `audit/recovery_plan.md`, and `audit/result_reproducibility.md`.

---

## 1. Purpose of This Archive

This directory (`legacy/`) preserves historical prototypes, experimental scripts, and documentation developed during earlier iterations of the TriNetra project.

As documented in the forensic audits:
1. **Template-Generated Complaints:** The datasets contained herein (e.g., `legacy/datasets/customer_complaints_dataset.csv`, `legacy/datasets/trinetra_real_complaints_expanded.csv`, `legacy/data/`) consist of programmatic text templates and synthetic records rather than authentic scraped consumer disputes.
2. **Circular Telemetry & Rigged Baselines:** Phase 1 experiments (`legacy/phase-1/`) and validation scripts (`legacy/validation_output/`) evaluated algorithms against synthetic data where failure modes were hardcoded by the companion generator and baselines were artificially constrained, resulting in circular metrics (e.g., perfect $F_1 = 1.000, p < 10^{-15}$).
3. **Simulated Offline Fallbacks:** Legacy validation scripts contained simulation routines that reported fabricated latencies and accuracies when backend services were offline.

---

## 2. Retention Policy & Scientific Integrity

In accordance with scientific integrity guidelines:
- **No Deletion / Git History Rewrite:** This material is preserved to maintain a complete, unbroken audit trail and support academic reproducibility audits.
- **Strict Quarantine:** Nothing in `legacy/` should be imported, executed, cited, or incorporated into active research papers or benchmarks.
- **Active Research Core:** All active research and reproducible experiments are located in `trinetra_link/` and evaluated under the preregistered protocols in `research/reviewed_v2/`.

---

## 3. Contents Inventory

- `legacy/phase-1/`: Legacy Python reconciliation engine, normalizers, and synthetic test suites.
- `legacy/phase-2/`: Spring microservices, dispute console, and mock fraud detection services.
- `legacy/phase-3/`: Locust load testing assets and synthetic traffic profiles.
- `legacy/xscrapper/`: Legacy literature mining scrapers and unverified scraping logs.
- `legacy/datasets/`: Quarantined template complaint CSVs.
- `legacy/data/`: Quarantined Phase 1 feature matrices and circular prediction CSVs.
- `legacy/results/`: Archived Phase 1 evaluation runs and confusion matrices.
- `legacy/validation_output/`: Archived output from legacy real_world_validation runs.
- `legacy/notes/`: Raw ChatGPT prompt transcripts and informal developer notes.
- `legacy/TriNetra AI Documentation/`: Legacy documentation and high-level project slides.
- `legacy/TRINETRA_*.md`: Superseded project specifications and production blueprints.
