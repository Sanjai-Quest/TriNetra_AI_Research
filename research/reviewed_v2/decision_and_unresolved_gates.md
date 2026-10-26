# Formal Decision Framework & Prioritized Verification Gates (Reviewed v2.5)

> **Document Type:** Research Governance & Stage Gate Decision Framework  
> **Audit Version:** Reviewed v2.5 (Residual Defect Closure Update)  
> **Date:** 2026-10-24  
> **Reviewer Role:** Independent Senior Research-Methodology Reviewer  
> **Formal Recommendation:** **CONDITIONAL PIVOT**  
> **Operational Status:** Physical Experiment Execution Gated / Frozen Pending Compliance  

---

## 1. Formal Recommendation: CONDITIONAL PIVOT

The project decision is formally rendered as **CONDITIONAL PIVOT**.

### 1.1 Why a Unconditional "GO" is REJECTED
An unconditional "GO" decision is methodologically unjustified. The audit establishes that:
1. Novelty is **not proven**: Database queries for Q01, Q05, and Q06 lack exported citation logs, and adjacent literature (Shiyamaladevi & Aparajeeta 2025 on OBD vision; Elia et al. 2024 on warehouse anomaly detection) already addresses individual checkpoints.
2. Legal records for Rangareddy rely on **secondary commercial news reporting** with unconfirmed docket numbers, rather than certified primary orders.
3. The planned 60-unit physical experiment cannot provide confirmatory statistical power or national generalizability.

### 1.2 Why a "DEFER" is UNNECESSARY
A total deferral or project abandonment is unnecessary because:
1. The **operational problem is real and severe**: Adjudicated court cases (*Adilabad* C.C. 187/2025; *Kurnool* C.C. 18/2026) confirm that lack of handover evidence causes massive corporate liabilities and consumer harm.
2. The **strategic scope pivot is sound**: Permanently excluding Direction 2 (saturated pre-delivery return forecasting) eliminates redundant work.
3. The **conceptual gap is coherent**: No identified study in operations research (Mishra & Dutta 2026) or computer vision (Shiyamaladevi 2025) formulates an end-to-end evidence linking and selective prediction model across noisy field handovers.

### 1.3 Core Terms of the CONDITIONAL PIVOT
- **Direction Anchored:** TriNetra will focus exclusively on **Direction 1: Handover Evidence Continuity & Cross-Stage Discrepancy Attribution** across forward OBD, return pickup, and warehouse receiving.
- **Novelty Language Moderated:** No claims of "universal novelty" or "pioneering first study" will be made. The contribution is strictly framed as an exploratory investigation into cross-stage observation degradation and selective prediction.
- **Physical Data Collection Frozen:** The Phase 1 experimental protocol ([`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md)) will **not be executed physically** until Pre-Experimental Gates E-1, E-2, and E-3 are satisfied.

---

## 2. Prioritized Verification Gates

To prevent creating an artificial, indefinite block on running a physical pilot over secondary legal court records or unindexed working papers, the verification gates are formally separated into two distinct operational categories:

```
┌────────────────────────────────────────────────────────────────────────┐
│ [CATEGORY A] PRE-EXPERIMENTAL GATES                                    │
│ Mandatory technical and governance requirements that MUST be cleared   │
│ BEFORE physical package staging and reviewer sessions may begin.       │
├────────────────────────────────────────────────────────────────────────┤
│ • Gate E-1: Protocol Freeze & Preregistration Commit                   │
│ • Gate E-2: Truth Ledger Hash Manifest Pre-Commitment (Embargoed Truth) │
│ • Gate E-3: Reviewer Calibration Trial & Baseline Agreement Check      │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [CATEGORY B] PRE-PUBLICATION / MANUSCRIPT GATES                        │
│ Methodological requirements that MUST be cleared BEFORE final paper    │
│ submission, but DO NOT block running the physical pilot.               │
├────────────────────────────────────────────────────────────────────────┤
│ • Gate M-1: Primary Certified Court Orders from eCourts Services       │
│ • Gate M-2: Export Receipts for Scopus/WoS Database Queries            │
│ • Gate M-3: Full-Text Acquisition of Bhattacharya Working Paper        │
│ • Gate M-4: Operations Research Conference Proceedings Screen          │
│ • Gate M-5: Full-Text Review of Elia et al. (2024) Prior-Art Clearance │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Pre-Experimental Gates (Must Be Cleared BEFORE Pilot Execution)

| Gate ID | Target Domain | Specific Gate Requirement | Verification Artifact Prepared | Current Status | Experimental Blocking Ruling |
|:---:|---|---|---|:---:|:---:|
| **Gate E-1** | Protocol Preregistration | Frozen protocol version (v2.5.0) with an independently timestamped public Git commit hash | [`preregistration_protocol_v2.5.md`](research/reviewed_v2/preregistration_protocol_v2.5.md) committed to Git | **CLEARED** | **UNBLOCKED** |
| **Gate E-2** | Ground-Truth Cryptography | SHA-256 hash manifest committed to Git before physical staging; plaintext truth ledger strictly embargoed until trial completion | [`ground_truth_commitment_manifest.json`](research/reviewed_v2/ground_truth_commitment_manifest.json) populated with verified hashes and committed | **CLEARED** | **UNBLOCKED** |
| **Gate E-3** | Reviewer Readiness | 10-case text-based rubric calibration completed with four real independent Reviewers $R_1-R_4$ (Fleiss' $\kappa \ge 0.60$); separate unscored UI familiarization | [`calibration_reviewer_pack_10.md`](research/reviewed_v2/calibration_reviewer_pack_10.md) & [`calibration_ratings_template.csv`](research/reviewed_v2/calibration_ratings_template.csv) prepared; trial unexecuted | **PENDING (Awaiting 4 Real Reviewers)** | **BLOCKING EXPERIMENT** |

> [!CAUTION]
> **Pre-Experimental Gating Ruling:**  
> Gates **E-1 and E-2 are formally CLEARED** via lead approval and Git commitment of the public hash manifest. Physical package staging, courier photo captures, and human reviewer adjudication remain **BLOCKED** strictly until Pre-Experimental Gate **E-3** is cleared by four real independent reviewers completing calibration with Fleiss' $\kappa \ge 0.60$. Simulated ratings and synthetic data remain strictly prohibited.

---

## 4. Pre-Publication / Manuscript Gates (Required Before Paper Submission)

These gates are necessary to support specific assertions in a formal academic publication, but **do not block execution of the physical exploratory pilot**:

| Gate ID | Target Domain | Specific Gate Requirement | Verification Standard | Current Status | Impact on Project |
|:---:|---|---|:---:|:---:|---|
| **Gate M-1** | Legal Citation Rigor | Procure certified primary orders for Adilabad (187/2025), Kurnool (18/2026), and Rangareddy (*T. Pranav Rao*) via eCourts India registry | Level 6 (Primary Court Order) | **OPEN (SECONDARY REPORTING)** | Required for citing judicial text in final manuscript. Does NOT block physical packaging experiment. |
| **Gate M-2** | Search Rigor Export | Automated export receipts (`.bib` / `.csv` citation manifests) for Queries Q01, Q05, Q06 from institutional terminals | Level A (Reproducible Database Export) | **OPEN (INTERACTIVE QUERY)** | Required for publishing systematic review. Does NOT block physical packaging experiment. |
| **Gate M-3** | Working Paper Verification | Procure complete manuscript of Bhattacharya (2026, SSRN 6803038) via interlibrary loan | Level 5 (Full Text Reviewed) | **OPEN (ABSTRACT ONLY)** | Required before citing dynamic game-theoretic proofs. Does NOT block physical packaging experiment. |
| **Gate M-4** | OR Conference Screen | Screen INFORMS, POMS, and SOM India (2023–2026) conference proceedings for adjacent reverse logistics papers | Level 5 (Proceedings Review) | **OPEN (UNSCREENED)** | Required before making definitive literature gap assertions in paper submission. |
| **Gate M-5** | Prior-Art Full-Text Clearance | Procure and review complete unredacted text of Elia et al. (2024, Emerald Insight) via university interlibrary loan | Level 5 (Full Text Reviewed) | **OPEN (ABSTRACT & SUMMARY REVIEWED)** | Required before finalizing manuscript literature review. Does NOT block physical packaging experiment; novelty claims remain bounded. |

---

## 5. Mandatory Governance Summary

1. **Physical Pilot Status:** **FROZEN.** No physical packages will be staged or human reviewers engaged until Gates E-1, E-2, and E-3 are fully executed.
2. **Application Code Status:** **FROZEN.** Application code, database schemas, and AI scrapers must not be modified.
3. **Data Integrity Rule:** Zero synthetic complaints, artificial URLs, or fabricated customer feedback may be ingested.
