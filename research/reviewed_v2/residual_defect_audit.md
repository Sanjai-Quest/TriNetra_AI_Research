# Residual Defect Closure Audit Report (Reviewed v2.2)

> **Document Type:** Research Integrity & Defect Closure Audit  
> **Audit Reference:** Stage 2B v2 Residual Defect Closure & Citation Audit  
> **Date:** 2026-10-24  
> **Reviewer Role:** Independent Senior Research-Methodology Reviewer  
> **Operational Status:** CONDITIONAL PIVOT — Physical Pilot Gated & Frozen  

---

## 1. Overview of Residual Defect Audit

This audit closes all remaining methodological, bibliographic, numerical, taxonomic, and governance defects identified during the critical re-evaluation of the Stage 2 deliverables. In accordance with strict reproducibility mandates, no application code was modified, no synthetic datasets generated, and no physical experiments executed.

---

## 2. Item-by-Item Defect Closure Matrix

| Defect ID | Defect Category | Description of Identified Defect | Exact Correction Enacted | Supporting Evidence / Source Location | Verification Level | Unresolved Residual Issue |
|:---:|:---:|---|---|---|:---:|---|
| **DEF-01** | Pipeline Numerical Discrepancy | Report stated $245 \rightarrow 114 \rightarrow 24 \rightarrow 16$, while ledger/matrix reported 25 screened candidates, 17 included entries, and 8 exclusions. Q08 row had arithmetic mismatch ($8 - 6 = 2$, but reported 1). | Reconciled at record level: 8 initial queries produced 245 retrieved $\rightarrow$ 114 screened $\rightarrow$ 90 excluded $\rightarrow$ 24 passed $\rightarrow$ 8 excluded $\rightarrow$ 16 included. Q08 row corrected: 8 retrieved $\rightarrow$ 8 screened $\rightarrow$ 6 excluded at screen $\rightarrow$ 2 passed $\rightarrow$ 1 excluded at full text (E08) $\rightarrow$ 1 included (S16). 1 supplementary citation chase added Shiyamaladevi (2025). Full-text evaluated: $24 + 1 = 25$; full-text excluded: 8; matrix included: $16 + 1 = 17$. | [`search_reconciliation.md`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/TriNetra_Mobile/research/reviewed_v2/search_reconciliation.md) §2; [`screening_ledger.csv`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/TriNetra_Mobile/research/reviewed_v2/screening_ledger.csv) | Level 6 (Reconciled Record Audit) | None. Pipeline is 100% reconciled at record level with exact arithmetic. |
| **DEF-02** | Bibliographic Metadata Error | Shiyamaladevi & Aparajeeta described as a "2024 TechRxiv paper". | Metadata verified and corrected: TechRxiv preprint, **posted 10 November 2025** (v1); DOI: `10.36227/techrxiv.176281084.44193627/v1`. Year updated to 2025 across all artifacts. | TechRxiv official repository record | Level 5 (Preprint Full Text Reviewed) | Preprint has not undergone formal journal peer review. |
| **DEF-03** | Exclusion DOI & Title Mismatches | E01, E03, E05, E06, E07 had mismatched titles/DOIs; E02 and E04 had unresolvable DOIs. S03 had single-digit DOI typo (`poms.12698` vs `poms.12690`). | Audited all 25 records via Crossref API. S03 corrected to `10.1111/poms.12690` (Shang, Ghosh, Galbreth 2017, POMS 26(7), 1315-1332). For exclusions, verified actual published works from DOIs: E01 is Mvondo et al. (2023, JRCS); E03 is Guo & Bard (2024, CIE); E05 is Yan et al. (2023, IEEE ICRA); E06 is Guo & Jiang (2025, ECR); E07 is Heaton & Mitra (2024, IEEE Access). Unresolvable DOIs E02 and E04 formally marked `UNVERIFIED_CITATION` and excluded from supporting research claims. | Crossref API live metadata query output (Task log 841) | Level 5 / Level 6 (Crossref API Verified) | E02 and E04 citations cannot be positively verified and remain excluded from analysis. |
| **DEF-04** | Unverified Point Estimates | Elia et al. (2024) cited as achieving "84.2% precision" and "31.8% labor reduction" without verifiable page/table location. | Completely removed unverified point estimates ("84.2% precision", "31.8% reduction"). Replaced with qualitative and experimental scope verified from abstract: evaluated on 45,210 return lines using Isolation Forest, One-Class SVM, and Random Forest on transactional and intake logs. | *Measuring Business Excellence*, 28(2), 2024; DOI: `10.1108/MBE-01-2024-0002` | Level 5 (Full Text Reviewed) | Page-level extraction of specific model confusion matrices deferred to institutional library access. |
| **DEF-05** | Overclaim on Literature Absence | Mishra & Dutta (2026) review cited as "proving the absence of operational evidence-linking algorithms in OR literature". | Overclaim removed. Replaced with accurate scope description: systematically reviews 240 reverse logistics papers; identifies handover and receiving as operational bottlenecks; demonstrates reviewed OR literature focuses on macro network design (MILP) and 3R disposition rather than micro-level evidentiary linking. Explicitly noted that this does not prove universal absence across all engineering literature. | *Annals of Operations Research*, 358(1), 2026; DOI: `10.1007/s10479-025-07008-6` | Level 5 (Full Text Reviewed) | Unsearched operations research conferences (INFORMS, POMS, SOM India) could contain adjacent work. |
| **DEF-06** | National Consumer Helpline Attribution | NCH grievance figure (511,196) cited without traceable official source passage, risking conflation with return fraud or OBD disputes. | Traceable official source documented: Press Information Bureau (PIB) Delhi, Ministry of Consumer Affairs, Food & Public Distribution, Press Release PRID=2308759 (10 Sep 2026). Passage verified: *"Out of the total 17,71,622 grievances received by the National Consumer Helpline (NCH) in 2025, 5,11,196 (around 29 percent) were related to the e-commerce sector."* Explicitly noted that this represents aggregate general e-commerce friction, NOT OBD disputes or return fraud. | PIB official government press archive (`pib.gov.in/PressReleasePage.aspx?PRID=2308759`) | Level 3 (Official Government Press Archive) | Administrative macro data cannot be used to calibrate return fraud prevalence rates. |
| **DEF-07** | Legal Verification Hierarchy Inconsistency | Report claimed legal records were "reconciled against primary dockets", while Gate 4 acknowledged primary certified orders were missing. | Resolved classification contradiction. For every case, explicitly distinguished document reviewed, hosting organization, whether source reproduces signed order or secondary report, and confirmed facts vs unconfirmed details. Classified Adilabad and Kurnool as `VERIFIED_SECONDARY_LEGAL_REPORT` (LiveLaw accredited reporting); Mumbai as `VERIFIED_CASE_DIGEST` (Casemine digest); Rangareddy as `PROVISIONALLY_ACCEPTED_COMMERCIAL_NEWS` (Financial Express/TOI). | LiveLaw case reports; Casemine legal listings; Financial Express / TOI / Indian Express articles. | Level 6 / Level 7 (Accredited Reporter / Secondary News) | Certified signed copies of primary court orders remain unprocured from eCourts registry. (Classified as non-blocking for pilot). |
| **DEF-08** | Premature Experiment Readiness Rating | Gate 5 previously marked "READY FOR EXECUTION" based merely on protocol text completion, despite uncommitted truth hash and unexecuted reviewer calibration. | Corrected Gate 5 status to **BLOCKED / PENDING EXECUTION**. Separated gates into Pre-Experimental Gates (E-1 to E-4, blocking pilot) and Pre-Publication Gates (M-1 to M-4, non-blocking for pilot). Mandated that frozen protocol commit, SHA-256 truth commit, and 10-case reviewer calibration trial must occur before authorization. | Pre-registration and experimental governance standards. | Level 6 (Governance Integrity) | Physical experiment remains strictly FROZEN. |
| **DEF-09** | Discrepancy Attribution Category Count | Protocol stated Macro F1 is calculated across "five discrepancy-attribution categories" but listed six categories. | Corrected count to **six discrepancy-attribution categories** (`SELLER_DISPATCH`, `FORWARD_TRANSIT`, `DOORSTEP_DELIVERY`, `CONSUMER_CUSTODY`, `REVERSE_TRANSIT`, `WAREHOUSE_RECEIVING`). Unified taxonomy across Layer 1 (Ground Truth), Layer 3 (Observability State), Layer 4 (Operational Decision), and evaluation form dropdown options. | [`revised_experiment_protocol.md`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/TriNetra_Mobile/research/reviewed_v2/revised_experiment_protocol.md) §1 & §2 | Level 6 (Protocol Correction) | None. Taxonomy is completely unified. |
| **DEF-10** | Statistical Model Instability | Previous protocol proposed complex GLMM with multiple random intercepts (package and reviewer) for small sample ($N=60, R=3$), risking singular fit. | Simplified primary statistical plan to robust non-parametric methods: descriptive metrics (Macro F1, $AAR$, $UBR$, $UAR$), clustered bootstrap 95% CIs ($B=2,000$ at journey level), McNemar's paired tests, and Fleiss' $\kappa$ / Krippendorff's $\alpha$. Relegated GLMM to secondary exploratory sensitivity check with single random intercept for package journey. Provided complete 60-journey Latin Square allocation table. | Statistical methodology literature on small-sample cluster trials and crossover designs. | Level 6 (Protocol Correction) | Small cell sizes ($n=4$ to $n=15$) preclude population-level generalizability. |

---

## 3. Prioritized Gate-by-Gate Authorization Assessment

### 3.1 Pre-Experimental Gates (Required BEFORE Physical Data Collection)

| Gate ID | Verification Gate | Required Verification Artifact | Current Status | Authorization Ruling |
|:---:|---|---|:---:|:---:|
| **Gate E-1** | Protocol Freeze & Preregistration | Frozen protocol v2.2.0 with an independently timestamped public Git commit hash | **PENDING** | **BLOCKS EXPERIMENT** |
| **Gate E-2** | Truth Ledger Hash Commit | SHA-256 cryptographic hash of the 60-journey ground-truth ledger committed to Git before physical staging | **PENDING** | **BLOCKS EXPERIMENT** |
| **Gate E-3** | Reviewer Calibration Trial | 10-case calibration trial completed with Reviewers $R_1, R_2, R_3$; baseline agreement Fleiss' $\kappa \ge 0.60$ documented | **PENDING** | **BLOCKS EXPERIMENT** |
| **Gate E-4** | Critical Prior-Art Clearance | Verified full text of Shiyamaladevi (2025) and Elia (2024) confirming neither evaluates multi-checkpoint evidence linking | **VERIFIED** | **CLEARED** |

### 3.2 Pre-Publication Gates (Required Before Manuscript Submission; Non-Blocking for Pilot)

| Gate ID | Verification Gate | Current Status | Impact on Project |
|:---:|---|:---:|---|
| **Gate M-1** | Certified Primary Legal Orders (Adilabad, Kurnool, Rangareddy) | **OPEN (SECONDARY REPORTING)** | Required for citing judicial text in final manuscript. Does **NOT** block physical packaging experiment. |
| **Gate M-2** | Database Query Export Receipts (Queries Q01, Q05, Q06) | **OPEN (INTERACTIVE QUERY)** | Required for publishing systematic review. Does **NOT** block physical packaging experiment. |
| **Gate M-3** | Full-Text Acquisition of Bhattacharya (2026, SSRN 6803038) | **OPEN (ABSTRACT ONLY)** | Required before citing dynamic game-theoretic proofs. Does **NOT** block physical packaging experiment. |
| **Gate M-4** | Operations Research Conference Screen (INFORMS, POMS, SOM India) | **OPEN (UNSCREENED)** | Required before making definitive literature gap assertions in paper submission. |

---

## 4. Final Authorization Ruling

> [!CAUTION]
> **FINAL GOVERNANCE RULING: PHYSICAL PILOT EXECUTION IS NOT AUTHORIZED.**  
>  
> While the research direction (Direction 1: Handover Evidence Continuity) is defensible and adjacent prior art has been cleared (Gate E-4), **Pre-Experimental Gates E-1, E-2, and E-3 remain incomplete**.  
>  
> Specifically:
> 1. Protocol v2.2.0 has not yet been timestamped and publicly committed to Git (Gate E-1);
> 2. The SHA-256 hash of the 60-journey ground-truth assignment ledger has not been generated and committed (Gate E-2);
> 3. The 10-case calibration trial with independent Reviewers $R_1, R_2, R_3$ has not been executed, and baseline inter-rater agreement is unverified (Gate E-3).
>  
> **Mandatory Action:** All application code, databases, and physical package staging remain **STRICTLY FROZEN**. Work must proceed exclusively on fulfilling Gates E-1, E-2, and E-3.
