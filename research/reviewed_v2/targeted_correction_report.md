# Targeted Source, Screening, and Protocol Correction Report (Reviewed v2.3)

> **Document Type:** Research Integrity & Defect Closure Report  
> **Date:** 2026-10-24  
> **Reviewer Role:** Independent Senior Research-Methodology Reviewer  
> **Scope:** Final Targeted Corrections Across `research/reviewed_v2/`  
> **Operational Status:** CONDITIONAL PIVOT — Physical Experiment Strictly Frozen  

---

## 1. Summary of Targeted Corrections Enacted

| Defect Item | Original Identified Problem | Targeted Correction Enacted | Verification Evidence / Reference |
|---|---|---|---|
| **1. E02 & E04 Classification** | Counted as full-text exclusions despite unverified identities and inaccessible full texts. | Reclassified from full-text exclusions to **`UNRETRIEVED_UNVERIFIED_CANDIDATE`** (`full_text_reviewed: NO`). Full-text exclusions reduced from 8 to **6** verified documents. | [`screening_ledger.csv`](research/reviewed_v2/screening_ledger.csv) |
| **2. Search Record Verification Distinction** | Pipeline implied entire 246-record literature search was record-level verified despite missing database export receipts. | Separated evidence base into **Tier 1 (23 Record-Level Verified Sources)**, **Tier 2 (2 Unretrieved Candidates)**, and **Tier 3 (Unverified Summary Log Counts)**. Explicitly disclosed that the 245 retrieved and 90 screen-excluded counts derive from summary logs, not raw exported files. | [`search_reconciliation.md`](research/reviewed_v2/search_reconciliation.md) §1 & §3 |
| **3. Isolating Evidence Linkage from Quantity** | Condition C received more information than Baselines A and B, confounding the effect of linkage with the effect of additional evidence. | Restructured into a **4-condition design**: **Condition C (Baseline 2: Disconnected Multi-Point)** receives all 4 checkpoints with linkage withheld (information-matched control). **Condition D (Proposed System)** receives identical underlying evidence with linkage provided. Comparison D vs. C isolates **linkage**; C vs. A/B isolates **quantity**. | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §4 |
| **4. Taxonomy & Conceptual Layer Separation** | Same terminology used across physical events, observations, reviewer dropdowns, and operational decisions. | Established **dedicated non-overlapping vocabularies**: Physical Ground Truth ($\mathcal{G}$: `GT_*`), Observability State ($\Omega$: `OBS_*`), Reviewer Attribution ($\mathcal{A}$: `ATTR_*`), and Operational Decision ($\mathcal{D}$: `DEC_*`). Primary and abstention metrics formally defined using these distinct fields. | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §2 & §6 |
| **5. S03 DOI Typo Correction** | S03 had single-digit typo `10.1111/poms.12698` (Dong et al.). | Corrected to **`10.1111/poms.12690`** (Shang, Ghosh, Galbreth 2017, POMS, 26(7), pp. 1315–1332; Crossref verified). | [`validated_closest_work_matrix.csv`](research/reviewed_v2/validated_closest_work_matrix.csv) |

---

## 2. Reconciled Screening Pipeline Flow

$$\begin{aligned}
\text{Summary Log Retrieved (Q01–Q08)} &= 245 \\
\text{Summary Log Screened (Title/Abstract)} &= 114 \\
\text{Summary Log Screen-Excluded} &= 90 \\
\text{Candidates Seeking Full Text from Queries} &= 24 \\
\text{Unretrieved / Unverified Candidates} &= 2 \text{ (E02, E04 — Excluded Prior to Full Text)} \\
\text{Query Records Evaluated at Full Text} &= 22 \\
\text{Verified Full-Text Exclusions} &= 6 \text{ (E01, E03, E05, E06, E07, E08)} \\
\text{Matrix Included from Queries} &= 16 \\
\text{Supplementary Citation Search Included} &= 1 \text{ (S17: Shiyamaladevi & Aparajeeta, 2025)} \\
\mathbf{Total\ Verified\ Full\text{-}Text\ Evaluations} &= 22 + 1 = \mathbf{23} \\
\mathbf{Total\ Verified\ Full\text{-}Text\ Exclusions} &= \mathbf{6} \\
\mathbf{Total\ Unretrieved\ Candidates} &= \mathbf{2} \\
\mathbf{Total\ Included\ Matrix\ Records} &= 16 + 1 = \mathbf{17}
\end{aligned}$$

---

## 3. Dedicated Vocabularies Across Conceptual Layers

```
Layer 1: Ground Truth (𝒢)         Layer 3: Observability (Ω)       Layer 4: Reviewer Attribution (𝒜)
• GT_INTACT                      • OBS_DETERMINABLE               • ATTR_CONFIRMED_LEGITIMATE
• GT_FORWARD_TRANSIT_DAMAGE      • OBS_INDISTINGUISHABLE          • ATTR_STAGE_FORWARD_TRANSIT
• GT_DOORSTEP_SUBSTITUTION       • OBS_DEGRADED_INCOMPLETE        • ATTR_STAGE_DOORSTEP_DELIVERY
• GT_CUSTOMER_TAMPER                                              • ATTR_STAGE_CONSUMER_CUSTODY
• GT_REVERSE_TRANSIT_TAMPER                                       • ATTR_STAGE_REVERSE_TRANSIT
[EXCLUDED: GT_VENDOR_DEFECT,                                      • ATTR_STAGE_OTHER_OUTSIDE_SCOPE
 GT_WAREHOUSE_HANDLING_DAMAGE]                                    • ATTR_ABSTAIN_INDISTINGUISHABLE
                                                                  • ATTR_ABSTAIN_DEGRADED

Layer 5: Operational Decision (𝒟)
• DEC_APPROVE_REFUND             • DEC_REJECT_REFUND              • DEC_HOLD_INVESTIGATION
• DEC_CHARGEBACK_CARRIER         • DEC_CHARGEBACK_VENDOR
```

---

## 4. Multi-Tier Independent Validation Report

In strict compliance with audit instructions, **structural validation is reported separately from bibliographic and methodological validation**.

### 4.1 Structural Validation Report (Automated CSV & Code Parsing)
- **Tool:** Automated Python verification script (`csv.DictReader`).
- **`validated_closest_work_matrix.csv`:**
  - Structure: Exactly 17 data rows, 19 columns.
  - Column alignment: 100% consistent across all rows; zero misaligned delimiters or trailing commas.
  - Syntax Errors: **0**.
- **`screening_ledger.csv`:**
  - Structure: Exactly 25 data rows (17 included + 6 verified excluded + 2 unretrieved candidates), 15 columns.
  - Column alignment: 100% consistent across all rows.
  - Syntax Errors: **0**.
- **`claim_evidence_ledger.csv`:**
  - Structure: Exactly 13 data rows, 9 columns.
  - Column alignment: 100% consistent across all rows.
  - Syntax Errors: **0**.
- **Structural Validation Finding:** PASS. All artifact CSVs are structurally sound, well-formed, and programmatically valid.

### 4.2 Bibliographic Validation Report (Fact-Checking & Source Authentication)
- **Academic DOIs (Crossref REST API Audit):**
  - S01–S04, S06–S07, S09–S11, S17: 10 DOIs verified live against Crossref API with 100% title, author, year, and venue match.
  - S03 DOI: Corrected from typo `10.1111/poms.12698` to authentic `10.1111/poms.12690` (Shang et al., 2017).
  - S05: Bhattacharya (2026), SSRN 6803038 verified as valid abstract URL (HTTP 403 on full text; abstract-only review).
  - S17: Shiyamaladevi & Aparajeeta (2025), TechRxiv preprint verified (posted 10 Nov 2025).
  - Full-Text Exclusions: E01, E03, E05, E06, E07, E08 authenticated via live Crossref DOIs/official archives as authentic published papers evaluated against formal exclusion criteria.
  - Unretrieved Candidates: E02 and E04 failed DOI resolution and were reclassified as `UNRETRIEVED_UNVERIFIED_CANDIDATE`.
- **Legal Precedents:**
  - Mumbai (CC/132/2022): Verified via Casemine digest.
  - Adilabad (C.C. 187/2025): Verified via LiveLaw accredited report.
  - Kurnool (C.C. 18/2026): Verified via LiveLaw accredited report.
  - Rangareddy (*T. Pranav Rao*, order 21 Sep 2026): Verified via Financial Express/TOI; numeric CC docket unconfirmed. Certified court copies not in hand.
- **Corporate Policy & Government Archive:**
  - Flipkart OBD Terms (2026): Verified via live corporate portal.
  - PIB Press Release PRID=2308759: Verified via official government press archive.
- **Bibliographic Validation Finding:** CONDITIONAL PASS (All retained records verified; certified court copies and Q01/Q05/Q06 database export manifests pending).

### 4.3 Methodological Validation Report (Experimental Rigor & Epistemology)
- **Experimental Isolation:**
  - Confounding between evidence quantity and cross-stage linkage eliminated via Condition C (all 4 checkpoints provided without linkage) as an information-matched control against Condition D (all 4 checkpoints provided with linkage).
- **Epistemological Separation:**
  - Ground Truth ($\mathcal{G}$), Observability State ($\Omega$), Reviewer Attribution ($\mathcal{A}$), and Operational Decision ($\mathcal{D}$) are separated into distinct non-overlapping vocabularies.
  - Primary outcomes and abstention metrics ($AAR$, $UBR$, $UAR$, $ODA$) are defined using formal mapping equations across these separate fields.
- **Economic Figures:**
  - Platform-wide savings and cost figures explicitly reclassified as uncalibrated sensitivity parameters; not treated as empirical findings.
- **Methodological Validation Finding:** PASS for protocol coherence; EXECUTION REMAINS FROZEN.

---

## 5. Research-Readiness Gate Assessment & Final Verdict

| Gate ID | Requirement | Status | Verdict |
|:---:|---|:---:|:---:|
| **Gate E-1** | Protocol Freeze & Public Preregistration Commit | Git commit pending | **FAIL** |
| **Gate E-2** | Ground-Truth Ledger Cryptographic SHA-256 Commit | SHA-256 commit pending | **FAIL** |
| **Gate E-3** | 10-Case Reviewer Calibration Trial ($\kappa \ge 0.60$) | Reviewers uncalibrated | **FAIL** |
| **Gate E-4** | Critical Prior-Art Boundary Clearance | Shiyamaladevi/Elia verified | **PASS** |

### Definitive Governance Ruling: **PHYSICAL PILOT EXECUTION IS STRICTLY BLOCKED (FAIL)**

The research direction remains **CONDITIONAL PIVOT**. While the protocol and evidence base are now methodologically sound and internally coherent, physical execution remains **FROZEN** until Gates E-1, E-2, and E-3 are completed.
