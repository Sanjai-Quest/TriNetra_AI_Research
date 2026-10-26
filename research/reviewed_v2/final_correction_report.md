# TriNetra Research Stage 2: Final Targeted Correction Report (v2.4)

> **Document Type:** Independent Methodology & Evidence Verification Defect Closure Report  
> **Protocol & Matrix Version:** Reviewed v2.4 (Definitive Preregistration Baseline)  
> **Date:** 2026-10-24  
> **Reviewer Role:** Independent Senior Research-Methodology Reviewer  
> **Scope:** Targeted Defect Closure Across `research/reviewed_v2/`  
> **Governance Ruling:** **CONDITIONAL PIVOT — Physical Experiment Strictly Frozen**  

---

## 1. Itemized Defect Identification & Exact Corrections Enacted

| Defect ID & Item | Original Identified Problem | Exact Correction Enacted | Supporting Source / Protocol Location |
|---|---|---|---|
| **DEF-01: John et al. (2020) Bibliographic & Methodological Misattribution** | Matrix cited author as "Johna, S.", attributed ensemble ML (Random Forest, Gradient Boosting), 185,000 transactions, AUC 0.81 vs 0.64, and customer return abuse. | Corrected author to **John, S., Shah, B. J., & Kartha, P. (2020)**. Reclassified topic to **agent-assisted refund fraud analytics** in customer service. Removed unverified transaction counts and ML algorithms. Documented verified methodology: **penalised-likelihood logistic regression (Firth's penalised regression)** for rare-event fraud detection to isolate high-risk audit samples. Reclassified accessibility to `ABSTRACT_ONLY_REVIEWED` (Level 4). | [`validated_closest_work_matrix.csv`](research/reviewed_v2/validated_closest_work_matrix.csv#L4); *Journal of Business Analytics* 3(1), pp. 56–66; DOI: `10.1080/2573234X.2020.1776164` |
| **DEF-02: Elia et al. (2024) Unverified Numerical Claims** | Matrix claimed dataset of "45,210 return order lines" and specific ML models (Isolation Forest, One-Class SVM). | Removed unverified numerical transaction counts and specific model architectures. Documented verified qualitative and quantitative case study framework for reverse logistics anomaly detection at warehouse receiving, categorized across discrepancy causes/types and evaluated on operational dimensions (time savings, data accuracy, completeness, cost efficiency). Reclassified to `ABSTRACT_AND_CASE_STUDY_SUMMARY_REVIEWED` (Level 4). | [`validated_closest_work_matrix.csv`](research/reviewed_v2/validated_closest_work_matrix.csv#L3); *Measuring Business Excellence* 28(2); DOI: `10.1108/MBE-01-2024-0002` |
| **DEF-03: Bhavya (2025), Kar (2024), & Saxena (2025) Unverified Figures** | Unverified point estimates ("1,240 hardware tickets", "14.2 days dispute delay", regression Beta 0.412, percentage splits) appeared in matrix. | Pruned all unsupported numerical point estimates. Documented verified empirical survey and case study findings: Bhavya (hardware return disputes in Bengaluru), Kar (questionnaire survey on return triggers), Saxena (latent class analysis of return policy promises and constraints under Mental Accounting Theory). Saxena reclassified to `ABSTRACT_ONLY_REVIEWED` (Level 4). | [`validated_closest_work_matrix.csv`](research/reviewed_v2/validated_closest_work_matrix.csv#L9-L12) |
| **DEF-04: Ground-Truth Scenario Taxonomy Discrepancy** | Protocol proposed 6 discrepancy classes for primary Macro F1, but scenario allocation table allocated zero journeys to `GT_VENDOR_DEFECT` and `GT_WAREHOUSE_HANDLING_DAMAGE`. | **Narrowed primary classification estimand to the 4 physical handover discrepancy classes actually staged**: `GT_FORWARD_TRANSIT_DAMAGE`, `GT_DOORSTEP_SUBSTITUTION`, `GT_CUSTOMER_TAMPER`, `GT_REVERSE_TRANSIT_TAMPER`. Explicitly designated `GT_VENDOR_DEFECT` and `GT_WAREHOUSE_HANDLING_DAMAGE` as **outside the Phase 1 pilot estimand**. Synchronized ground-truth schema, scenario allocation ($N=60$), dropdown options, formulas, and metric definitions. | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §1.2, §2, §3.2, §6 |
| **DEF-05: Condition C vs D Authentication Confound** | Condition D received an additional "cryptographic chain-of-custody verification seal" that Condition C lacked, confounding cross-stage linkage with perceived data authenticity. | **Equalized cryptographic authenticity metadata across Conditions C and D**: Both conditions display identical SHA-256 tamper-evident verification stamps on each checkpoint record. The SOLE experimental manipulation between C and D is the presentation of cross-stage linkage (Condition C = disconnected unaligned tabs; Condition D = unified chronological timeline, aligned visual deltas, tare weight trajectory curve). | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §4.1, §4.2 |
| **DEF-06: McNemar's Test Inappropriate for Macro F1** | Protocol proposed using McNemar's test to compare multiclass Macro F1 between Conditions C and D. | Replaced McNemar's test on Macro F1 with **clustered bootstrap resampling ($B=2,000$ iterations) resampled at the package journey level ($J_i$)** to derive 95% percentile confidence intervals for $\Delta\text{Macro F1}$, paired with a non-parametric permutation test. Restricted McNemar's paired test strictly to paired binary outcomes (Binary Accuracy on determinable journeys; Binary Abstention on ambiguous journeys). | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §7.1 |
| **DEF-07: Redundant Metric Definition ($UBR = 1 - AAR$)** | Defining $UBR = 1 - AAR$ created mathematical redundancy between metrics intended to measure different behaviors. | **Redefined $AAR$, $UBR$, and $UAR$ independently**: $AAR$ measures appropriate abstention on ambiguous cases; $UBR$ measures unsupported blame on ambiguous cases; $UAR$ measures unnecessary abstention on determinable cases. Explained why $AAR + UBR \le 1$ (due to false confirmation of legitimacy or unrated timeouts). Defined explicit denominators and treatment of intact journeys. | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §6.2, §6.3 |
| **DEF-08: Rater Agreement Confounded Across Conditions** | Calculating pooled Fleiss' kappa across reviewers in the Latin Square design confounded rater agreement with experimental condition effects. | Clarified that pooled Latin Square kappa violates exchangeability. **Restricted Fleiss' kappa ($\kappa \ge 0.60$) and Krippendorff's alpha strictly to the Pre-Experimental Calibration Trial (Gate E-3)** where all 4 reviewers evaluate identical benchmark journeys under identical conditions. Main trial reviewer variance modeled via Generalized Linear Mixed-Effects Models (GLMM). | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §7.3; [`decision_and_unresolved_gates.md`](research/reviewed_v2/decision_and_unresolved_gates.md) §3 |

---

## 2. Trade-Off Analysis & Justification for the 4-Class Pilot Estimand

In designing the Phase 1 exploratory pilot ($N=60$ independent package journeys), two taxonomic options were evaluated:

### Option A: Six Discrepancy Classes across $N=60$
- Staging 6 discrepancy classes (`GT_VENDOR_DEFECT`, `GT_FORWARD_TRANSIT_DAMAGE`, `GT_DOORSTEP_SUBSTITUTION`, `GT_CUSTOMER_TAMPER`, `GT_REVERSE_TRANSIT_TAMPER`, `GT_WAREHOUSE_HANDLING_DAMAGE`) plus intact journeys, degraded sensor cases, and ambiguous cases across $N=60$ would force cell sizes down to $n \le 4$.
- Small cells generate severe sampling noise, producing high variance in class-specific F1 scores and making inter-condition statistical comparisons uninterpretable.
- Latent vendor defects cannot be observed at $CP_1$ seller dispatch without breaking factory seals, and post-intake warehouse handling damage occurs inside warehouse sortation after $CP_4$ intake, falling outside the transport handover sensing envelope.

### Option B: Four Physical Handover Discrepancy Classes (CHOSEN DESIGN)
- Aligns the primary estimand directly with the **four physical handover transitions** connecting dispatch, delivery, and return:
  1. Forward Transit Damage ($CP_1 \rightarrow CP_2$);
  2. Doorstep Delivery Substitution ($CP_2$ handover);
  3. Consumer Custody Tampering ($CP_2 \rightarrow CP_3$);
  4. Reverse Transit Tampering ($CP_3 \rightarrow CP_4$).
- Preserves robust cell sizes ($n = 8$ for core discrepancy classes, $n = 23$ for intact controls, $n = 8$ for degraded/ambiguous cases).
- Ensures that every staged physical journey directly tests the multi-checkpoint evidence-continuity intervention.
- Formally designates `GT_VENDOR_DEFECT` and `GT_WAREHOUSE_HANDLING_DAMAGE` as **outside the Phase 1 pilot estimand**, preventing uncalibrated staging and eliminating taxonomic misalignment.

---

## 3. Structural Validation Report (Separately Reported)

- **Verification Script:** Automated execution via Python `csv.DictReader` auditing delimiter integrity, row counts, column counts, and null field detection.
- **`validated_closest_work_matrix.csv`:**
  - Data rows: Exactly **17**.
  - Columns: Exactly **19**.
  - Syntax/Delimiter Errors: **0**.
  - Trailing/Misaligned fields: **0**.
  - Structural Verdict: **PASS**.
- **`screening_ledger.csv`:**
  - Data rows: Exactly **25** (17 included + 6 verified excluded + 2 unretrieved candidates).
  - Columns: Exactly **15**.
  - Syntax/Delimiter Errors: **0**.
  - Structural Verdict: **PASS**.
- **`claim_evidence_ledger.csv`:**
  - Data rows: Exactly **13**.
  - Columns: Exactly **9**.
  - Syntax/Delimiter Errors: **0**.
  - Structural Verdict: **PASS**.

---

## 4. Bibliographic Validation Report (Separately Reported)

Fact-checking and source authentication were evaluated independently from structural file parsing:

### 4.1 Academic Papers (Crossref API & Publisher Verification)
1. **Karl (2024):** DOI `10.1007/s11301-024-00436-x` verified live; systematic review of 25 return forecasting papers; Level 5 (Full-Text Reviewed).
2. **Elia et al. (2024):** DOI `10.1108/MBE-01-2024-0002` verified live; reverse logistics anomaly detection case study; unverified transaction numbers removed; Level 4 (Abstract & Summary Reviewed).
3. **John, Shah, & Kartha (2020):** DOI `10.1080/2573234X.2020.1776164` verified live; *Journal of Business Analytics* 3(1), pp. 56–66; penalised-likelihood logistic regression for **agent-assisted refund fraud** in customer service; unverified ML algorithms/numbers removed; Level 4 (Abstract-Only Reviewed).
4. **Mishra & Dutta (2026):** DOI `10.1007/s10479-025-07008-6` verified live; review of 240 reverse logistics papers in *Annals of OR*; Level 5 (Full-Text Reviewed).
5. **Shang, Ghosh, & Galbreth (2017):** DOI `10.1111/poms.12690` verified live (corrected from typo `poms.12698`); analytical game-theoretic model of wardrobing and restocking fees in POMS; Level 5 (Full-Text Reviewed).
6. **King & Dennis (2006):** DOI `10.1108/13522750610671699` verified live; qualitative study using Theory of Planned Behaviour and accompanied deshopping interviews; Level 5 (Full-Text Reviewed).
7. **Bhattacharya (2026):** SSRN 6803038 verified as abstract listing; full text HTTP 403; Level 4 (Abstract-Only Reviewed).
8. **Kar, Das, & Mohapatra (2024):** DOI `10.17010/ijom/2024/v54/i5/173828` verified live; empirical survey on Indian return triggers; unverified regression beta estimates pruned; Level 5 (Full-Text Reviewed).
9. **Saxena, Chawla, & Richa (2025):** DOI `10.1108/IJPDLM-07-2024-0280` verified live; latent class analysis of Indian return policies under Mental Accounting Theory; Level 4 (Abstract-Only Reviewed).
10. **Shiyamaladevi & Aparajeeta (2025):** DOI `10.36227/techrxiv.176281084.44193627/v1` verified live; TechRxiv preprint posted **10 November 2025**; MobileNetV2 classifying OBD photos into 4 classes; Level 5 (Preprint Full-Text Reviewed).
11. **Bhavya (2025):** DOI `10.52783/jisem.v10i12s.1870` verified live; JISEM case study on hardware return disputes in Bengaluru; unsupported ticket counts/delay days pruned; Level 5 (Full-Text Reviewed).

### 4.2 Legal Precedents & Government Archives
12. **Flipkart OBD Terms (2026):** Verified via live corporate portal; Level 3 (Corporate Policy Verified).
13. **PIB Press Release PRID=2308759 (2026):** Official press archive confirmed; reports 511,196 aggregate e-commerce grievances on NCH (29% of 1,771,622 national complaints); Level 3 (Official Government Archive).
14. **Rushabh Maroo v. CrossBeats (Mumbai, CC/132/2022):** Casemine legal digest verified; Level 6 (Judgment Record Summary Verified).
15. **Rathod Swasthik v. Flipkart (Adilabad, C.C. 187/2025):** LiveLaw accredited legal report verified; Level 6 (Accredited Legal Reporter).
16. **Kodila Krishan Chaitanya v. Perfume 24x7 (Kurnool, C.C. 18/2026):** LiveLaw accredited legal report verified; Level 6 (Accredited Legal Reporter).
17. **T. Pranav Rao v. Platform (Rangareddy, Order 21 Sep 2026):** Financial Express/TOI news reports verified; numeric CC docket unconfirmed; certified court copy not in hand; Level 7 (Secondary Commercial News Report).

### 4.3 Full-Text Exclusions & Unretrieved Candidates
- **Verified Full-Text Exclusions ($n=6$):** E01 (Mvondo 2023, JRCS); E03 (Guo & Bard 2024, CIE); E05 (Yan 2023, IEEE ICRA); E06 (Guo & Jiang 2025, ECR); E07 (Heaton & Mitra 2024, IEEE Access); E08 (NCDRC 2025 Annual Report). All DOIs/URLs verified.
- **Unretrieved / Unverified Candidates ($n=2$):** E02 and E04 failed DOI resolution; reclassified as `UNRETRIEVED_UNVERIFIED_CANDIDATE` and excluded prior to full-text review.

---

## 5. Remaining Uncertainties & Scientific Boundaries

1. **Unretrieved Database Export Receipts (Queries Q01, Q05, Q06):** Interactive database session logs ($N=245$ retrieved, $n=90$ screen-excluded) lack raw `.bib`/`.csv` manifests. The literature review is formally disclosed as an **exploratory scoping search**, and TriNetra **does not claim universal novelty**.
2. **Certified Court Order Procurement:** Certified signed copies from the Adilabad, Kurnool, and Rangareddy registries remain unprocured via eCourts. Secondary legal journalism provides sufficient confidence for protocol design, but certified copies remain required under Pre-Publication Gate M-1.
3. **Exploratory Pilot Scope ($N=60$):** Findings from the 60-journey pilot cannot establish national fraud prevalence, courier compliance under commercial delivery pressure, or platform-wide financial savings. All economic figures are treated strictly as uncalibrated sensitivity parameters.

---

## 6. Pre-Experimental Readiness Gate Assessment & Final Verdict

| Gate ID | Requirement | Verification Artifact Required | Evaluation Finding | Verdict |
|:---:|---|---|---|:---:|
| **Gate E-1** | Protocol Freeze & Preregistration Commit | Timestamped Git commit hash of Protocol v2.4.0 on public repository | Git commit pending user repository action | **FAIL (PENDING)** |
| **Gate E-2** | Ground-Truth Cryptographic Pre-Commitment | SHA-256 cryptographic hash of 60-journey ground-truth ledger committed to Git before staging | Truth ledger uncommitted to Git | **FAIL (PENDING)** |
| **Gate E-3** | Reviewer Calibration Trial | 10-case calibration trial completed with Reviewers $R_1, R_2, R_3, R_4$ documenting Fleiss' $\kappa \ge 0.60$ | Reviewers uncalibrated | **FAIL (PENDING)** |
| **Gate E-4** | Critical Prior-Art Clearance | Verification that Shiyamaladevi (2025) and Elia (2024) do not evaluate multi-checkpoint linking | Full texts/abstracts verified; boundary confirmed | **PASS (CLEARED)** |

### Final Governance Ruling: **PHYSICAL PILOT EXECUTION IS STRICTLY BLOCKED (FAIL)**

The research direction remains **CONDITIONAL PIVOT**. All methodological, taxonomic, bibliographic, and statistical protocol defects are now completely resolved, and the protocol is methodologically sound and internally coherent.

In strict adherence to experimental integrity:
- **Zero application code was modified.**
- **Zero synthetic records were generated.**
- **Zero physical trials were conducted.**
- **The physical experiment remains FROZEN** until Pre-Experimental Gates E-1, E-2, and E-3 are formally executed and approved.
