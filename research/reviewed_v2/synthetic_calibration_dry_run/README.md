# TriNetra AI: Synthetic Reviewer Calibration Dry-Run Enclave

> **CRITICAL RESEARCH INTEGRITY NOTICE:**  
> **DOCUMENT CLASSIFICATION:** SYNTHETIC REHEARSAL FIXTURE — NOT HUMAN REVIEW DATA.  
> **GOVERNANCE STATUS:** The artifacts and ratings in this directory were created exclusively for synthetic calibration rehearsal, classification consistency testing, rubric diagnostic analysis, and analysis pipeline verification.  
> **OFFICIAL GATE STATUS:** Official Gate E-3 remains strictly **PENDING** until genuine independent human reviewers submit completed ratings. Physical package staging remains strictly **FROZEN**.

---

## Directory Purpose

This directory provides an isolated testing enclave to evaluate:
1. **Rubric Diagnostic Clarity:** Testing whether the TriNetra five-layer adjudication taxonomy and decision rules can be interpreted consistently by independent evaluative perspectives.
2. **Epistemic Edge Cases:** Diagnosing how different review strategies (evidence-first, alternative explanations, boundary tracking, noise filtering) respond to ambiguous, sensor-degraded, and conflicting telemetry.
3. **Pipeline Safety:** Verifying that the agreement calculation engine ([`compute_calibration_agreement.py`](research/reviewed_v2/compute_calibration_agreement.py)) correctly computes Fleiss' $\kappa$, decouples attribution from operational decisions, and rejects malformed or blank inputs.

---

## Inventory of Deliverables

| Deliverable File | Description | Classification |
|:---|:---|:---:|
| [`README.md`](./README.md) | Enclave overview, manifest, and governance restrictions | Documentation |
| [`agent_A_evidence_first.md`](./agent_A_evidence_first.md) | Profile & system instructions for Agent A (Evidence-First Reviewer) | Configuration |
| [`agent_B_alternative_explanations.md`](./agent_B_alternative_explanations.md) | Profile & system instructions for Agent B (Alternative-Explanation Reviewer) | Configuration |
| [`agent_C_journey_stage.md`](./agent_C_journey_stage.md) | Profile & system instructions for Agent C (Journey-Stage Reviewer) | Configuration |
| [`agent_D_uncertainty_abstention.md`](./agent_D_uncertainty_abstention.md) | Profile & system instructions for Agent D (Uncertainty & Abstention Reviewer) | Configuration |
| [`synthetic_case_pack.md`](./synthetic_case_pack.md) | 10 diagnostic mock return cases (`DRYRUN-01` to `DRYRUN-10`) | Synthetic Data |
| [`synthetic_agent_results.csv`](./synthetic_agent_results.csv) | 40 structured evaluations rendered by the four AI agents | Synthetic Ratings |
| [`synthetic_consistency_report.md`](./synthetic_consistency_report.md) | Diagnostic analysis of multi-agent agreement and classification divergences | Diagnostic Report |
| [`synthetic_pipeline_test_report.md`](./synthetic_pipeline_test_report.md) | Formal test report verifying agreement math, metric decoupling, and input validation | Test Report |
| [`run_synthetic_dry_run.py`](./run_synthetic_dry_run.py) | Python execution harness for isolated agent evaluation | Tooling / Script |
| [`test_analysis_pipeline_safety.py`](./test_analysis_pipeline_safety.py) | Test fixture verifying 4 safety suites against analytical benchmarks | Tooling / Script |

## Key Diagnostic Findings & Implementation Classification

1. **Implementation Nature (Deterministic Simulation):**
   - The four synthetic reviewers were executed as a **deterministic Python simulation** (pre-authored dictionary rule mappings for each profile), **not** independent model invocations or dynamic LLM agent calls.
   - Timing measurements record purely raw program dictionary-lookup duration (`execution_duration_sec`, $<10^{-5}\text{s}$) with all artificial timing offsets strictly removed.
2. **Synthetic Agreement Metrics:**
   - Attribution Assessment Fleiss' $\kappa_{\text{attr}} = \mathbf{0.8841}$ (Observed agreement: 90.0%, Chance: 13.8%).
   - Operational Decision Fleiss' $\kappa_{\text{dec}} = \mathbf{0.9337}$ (Observed agreement: 95.0%, Chance: 24.6%).
   - *Limitation:* These values measure concordance among pre-authored rule encodings across 10 mock cases. They do **not** establish AI reasoning reliability, absence of hallucinations, or human inter-reviewer reliability.
3. **Epistemic Divergences & Evidence Audit:**
   - **Case DRYRUN-03:** Disagreement between forward transit linehaul swap vs doorstep delivery presentation. (Audit revealed that detection at doorstep was inappropriately conflated with origin of swap).
   - **Case DRYRUN-04:** Audit revealed that stage attribution (`ATTR_STAGE_CONSUMER_CUSTODY`) was inappropriately conflated with proof of personal customer fraud.
   - **Case DRYRUN-10:** Disagreement between integrating depot scale drift audit logs (`ATTR_CONFIRMED_LEGITIMATE`) vs conservative sensor conflict hold (`ATTR_ABSTAIN_INDISTINGUISHABLE`).
4. **Pipeline Safety Verification:**
   - Verified that `compute_calibration_agreement.py` completely decouples attribution and decision metrics.
   - Verified that unexecuted templates, missing cells, illegal category labels, duplicate assessments, imbalanced cases, and datasets with $<4$ reviewers are trapped and rejected.
   - Verified exact analytical calculation against hand-calculated benchmark ($\kappa = 7/11 \approx 0.6364$).

---

## Boundaries & Strict Prohibitions

- **No Data Contamination:** The synthetic ratings in `synthetic_agent_results.csv` must NEVER be copied or merged into `calibration_ratings_template.csv` or `calibration_response_form_R[1-4].csv`.
- **No Gate Clearance:** These synthetic results do NOT satisfy Gate E-3. Gate E-3 remains PENDING awaiting genuine human reviewer ratings.
- **Physical Staging Hold:** Physical package staging remains strictly **FROZEN**.

