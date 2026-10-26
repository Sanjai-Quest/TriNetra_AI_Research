# Archive: Gate E-3 Human Reviewer Calibration Materials

> **STATUS: WITHDRAWN BY PROTOCOL AMENDMENT v2.6.0**  
> **Reference:** [`research/amendments/AMENDMENT_v2.6.md`](../amendments/AMENDMENT_v2.6.md) §1–§2.

---

## 1. Overview and Withdrawal Rationale

This directory archives the calibration exercise materials and individual reviewer response forms developed for **Gate E-3** under Protocol v2.5.0:
- `calibration_package_10.md` / `calibration_reviewer_pack_10.md`
- `calibration_ratings_template.csv`
- `calibration_response_form_R1.csv` through `R4.csv`

### Why Gate E-3 Was Withdrawn
Protocol v2.5.0 originally made the physical returns study conditional on four independent human reviewers completing a 10-case calibration pack with Fleiss' $\kappa \ge 0.60$. This gate existed exclusively to support a human-adjudicator laboratory study (Condition C vs. Condition D).

Under **Protocol Amendment v2.6.0**:
1. The human-adjudicator user study is deferred to future work.
2. The study design is an **algorithm and dataset** paper evaluating TriNetra-Link against five automated baselines (B1–B5) and ablations across 120 filmed journeys.
3. Ground truth derives objectively from the filmed staging log with determinability $\Omega^*$ established by deterministic rules committed prior to data collection.
4. Gate E-3 is formally **withdrawn**, and its materials are preserved here for historical auditability and potential future volunteer studies.
5. The Fleiss' and Cohen's Kappa analysis engine is retained in `research/reviewed_v2/compute_calibration_agreement.py` for optional two-person rule verification audits (`trinetra truth audit`).
