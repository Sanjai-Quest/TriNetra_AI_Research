# TriNetra Research Stage 2: Final Targeted Correction Report (Reviewed v2.5)

> **Document Type:** Independent Methodology, Evidence Verification, & Defect Closure Report  
> **Protocol & Matrix Version:** Reviewed v2.5.0 (Definitive Preregistration Baseline)  
> **Date:** 2026-10-24  
> **Reviewer Role:** Independent Senior Research-Methodology Reviewer  
> **Scope:** Residual Defect Closure Across `research/reviewed_v2/`  
> **Governance Ruling:** **CONDITIONAL PIVOT — Physical Experiment Strictly Frozen**  

---

## 1. Executive Summary & Defect Closure Status

This report documents the resolution of all remaining methodological, bibliographic, formulaic, and statistical defects identified in the TriNetra Stage 2 research artifacts under `research/reviewed_v2/`. 

All corrections preserve a strict audit trail, maintain complete conceptual layer separation, and adhere to the **CONDITIONAL PIVOT** governance directive. In strict compliance with instructions:
- **Zero application code has been modified.**
- **Zero synthetic datasets, artificial claims, or fabricated citations have been generated.**
- **Physical experiments remain strictly FROZEN** pending genuine completion of mandatory Pre-Experimental Gates E-1, E-2, and E-3.
- **Structural validation is reported strictly separately** from factual and methodological verification.

---

## 2. Itemized Correction Ledger (Defects 1 through 5)

| Correction Item | Specific Identified Defect | Exact Methodological & Documentary Correction Enacted | Supporting Artifact / File Location |
|---|---|---|---|
| **1. Cross-Artifact Synchronization of Source Accessibility & Review Levels** | John et al. (2020), Elia et al. (2024), and Saxena et al. (2025) were inconsistently reported across artifacts (e.g., claimed as `FULL_TEXT_REVIEWED: YES` in screening ledger, while paywalled in literature matrix). Furthermore, the obsolete v2.1 research gap assessment remained in place. | **Harmonized accessibility and review levels to Level 4 (paywalled / abstract / summary reviewed) across all six project artifacts**: (1) `validated_closest_work_matrix.csv`, (2) `screening_ledger.csv`, (3) `claim_evidence_ledger.csv`, (4) `search_reconciliation.md`, (5) `revised_research_gap.md`, and (6) this report. Reclassified John et al. (2020) and Saxena et al. (2025) as `ABSTRACT_ONLY_REVIEWED` (`full_text_reviewed: NO`). Reclassified Elia et al. (2024) as `ABSTRACT_AND_CASE_STUDY_SUMMARY_REVIEWED` (`full_text_reviewed: NO`). Explicitly updated `revised_research_gap.md` to v2.5, replacing obsolete mismatched citation names (Cui, Guo, Ren, Patel) with the authentic 17 sources. | [`screening_ledger.csv`](research/reviewed_v2/screening_ledger.csv#L3-L10); [`validated_closest_work_matrix.csv`](research/reviewed_v2/validated_closest_work_matrix.csv#L3-L10); [`claim_evidence_ledger.csv`](research/reviewed_v2/claim_evidence_ledger.csv#L2-L13); [`revised_research_gap.md`](research/reviewed_v2/revised_research_gap.md) |
| **2. Correct Scenario Reporting & Exact Cell Allocations** | Generalizing statements (e.g., "$n \ge 8$ per class" or "eight journeys per class") contradicted the protocol's actual scenario allocation table, where SC-06 has $n=5$. | **Enforced exact scenario counts and explicit denominators throughout all protocol text**: Exactly 8 forward-transit damage ($J_{24}-J_{31}$), 8 doorstep substitution ($J_{32}-J_{39}$), 8 standard customer tampering ($J_{40}-J_{47}$), and 5 reverse-transit tampering ($J_{48}-J_{52}$). Clarified that core discrepancy cell counts are 8, 8, 8, and 5 (total 29 determinable discrepancy journeys). Intact journeys total 23 ($n=15$ standard, $n=8$ bag-change). Ambiguous/degraded journeys total 8 ($n=4$ degraded, $n=4$ ambiguous). Total sample size is exactly $N=60$ independent package journeys. | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §1.2, §3.2, §6.2, §6.3 |
| **3. Narrowed C-versus-D Research Claim** | Condition D differs from Condition C in more than record linkage alone: Condition D automates side-by-side visual delta alignment (synchronized pan/zoom) and tare weight trajectory plotting with anomaly flags, which Condition C presents as disconnected, unaligned tabs. | **Formally narrowed the research claim to evaluate a combined intervention**: Explicitly defined the treatment as a *combined linked-evidence presentation and automated visual/weight reconciliation pipeline* versus an unaligned, disconnected presentation of the identical underlying evidence and identical SHA-256 authenticity stamps. Aligned all research questions, hypotheses, and protocol descriptions to this narrower, defensible scope. | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §1.1, §4.1, §4.2, §7.1; [`revised_research_gap.md`](research/reviewed_v2/revised_research_gap.md) §3 |
| **4. Repaired Outcome Formulas & Condition-Specific Observability** | Restricting Macro F1 to determinable cases created an invalid cross-condition comparison, because condition-specific observability causes Conditions C and D to have different eligible cases. Furthermore, using a condition-independent target $\Omega_i^*$ failed to account for the fact that the same journey may be determinable under Condition D (with visual alignment and weight curves) but ambiguous under Condition C (unaligned tabs). | **Defined primary outcomes across all 60 journeys using condition-specific observability $\Omega_{ik}^*$ and optimal policy $\mathcal{D}_{ik}^*$**: (1) *Overall Adjudication Accuracy ($OAA$)* defined across all $N=60$ journeys, scoring 1 for correct attribution on condition-determinable journeys ($\Omega_{ik}^* = \text{OBS\_DETERMINABLE}$) and 1 for appropriate abstention on condition-ambiguous/degraded journeys ($\Omega_{ik}^* \neq \text{OBS\_DETERMINABLE}$); (2) *Operational Decision Alignment ($ODA$)* defined across all $N=60$ journeys matching $\mathcal{D}_{ik}^* = \mathcal{D}^*(\mathcal{G}_i, \Omega_{ik}^*)$; (3) *Discrepancy Macro F1* redefined as a secondary conditional metric with $TP_c, FP_c, FN_c$ all evaluated over the coherent universe of all 60 journeys. | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §1.3, §1.4, §6.1–§6.3 |
| **5. Reassessed Statistical Model & Reviewer Fixed Effects** | Proposing a Generalized Linear Mixed-Effects Model (GLMM) with a random intercept for reviewers $v_j \sim \mathcal{N}(0, \sigma_{\text{reviewer}}^2)$ with only $R=4$ reviewers is statistically unstable (variance components cannot be reliably estimated from 4 clusters; high risk of singular fit or boundary estimates at zero). | **Replaced reviewer random effects with Reviewer Fixed Effects in a logistic regression model**: Modeled reviewers via 3 fixed dummy variables ($R_2, R_3, R_4$) against reference $R_1$, directly adjusting for individual reviewer skill and stringency without parametric variance assumptions. Primary inference conducted via *journey-level clustered bootstrap resampling ($B=2,000$ iterations)* and *paired permutation testing (5,000 permutations)*. Documented pilot limitations and disclaimed national generalizability. | [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md) §7.1–§7.3, §8 |

---

## 3. Deep-Dive on Methodological & Statistical Repairs

### 3.1 Reconciled Bibliographic Status for Paywalled Sources

To eliminate any ambiguity regarding literature review depth:

1. **John, Shah, & Kartha (2020), *Journal of Business Analytics*, 3(1), pp. 56–66 (DOI: `10.1080/2573234X.2020.1776164`):**
   - **Accessibility Status:** `ABSTRACT_ONLY_REVIEWED` (Level 4).
   - **Full-Text Reviewed:** `NO`.
   - **Verified Content:** Peer-reviewed article in Taylor & Francis journal. Authors develop penalised-likelihood logistic regression (Firth's penalised regression) to model agent-assisted refund fraud (internal call-center staff issuing fraudulent refunds) to isolate high-risk audit samples.
   - **Boundary Disclosure:** Focuses entirely on post-purchase customer-service financial transactions. Contains zero physical package inspection, zero computer vision, zero doorstep OBD, and zero logistics custody handover data. Unsupported numerical transaction counts ("185,000 transactions") and unverified ML architectures (Random Forest/GBDT) remain permanently excised.

2. **Elia, Ghiani, Manni, & Margherita (2024), *Measuring Business Excellence*, 28(2) (DOI: `10.1108/MBE-01-2024-0002`):**
   - **Accessibility Status:** `ABSTRACT_AND_CASE_STUDY_SUMMARY_REVIEWED` (Level 4).
   - **Full-Text Reviewed:** `NO`.
   - **Verified Content:** Emerald journal publication. Authors develop an anomaly detection framework at reverse logistics warehouse receiving for a single e-commerce company, categorizing return anomalies by operational causes, discrepancy types, and product lines to monitor returned goods and evaluate operational performance dimensions (time savings, data accuracy, completeness, cost efficiency).
   - **Boundary Disclosure:** Operates exclusively at a single echelon (warehouse intake) on tabular transaction features. Does not capture multi-actor handovers, forward doorstep photos, or transit weight curves. Specific unverified order counts ("45,210 return lines") and specific ML algorithms (Isolation Forest/One-Class SVM) remain permanently excised.

3. **Saxena, Chawla, & Richa (2025), *IJPDLM*, 55(5) (DOI: `10.1108/IJPDLM-07-2024-0280`):**
   - **Accessibility Status:** `ABSTRACT_ONLY_REVIEWED` (Level 4).
   - **Full-Text Reviewed:** `NO`.
   - **Verified Content:** Emerald journal publication. Stated-choice experiment and latent class analysis of Indian online shoppers examining consumer valuation of return policy promises and verification constraints grounded in Mental Accounting Theory.
   - **Boundary Disclosure:** Stated-preference survey under hypothetical scenarios; paywalled full text; does not observe operational physical delivery handovers. Unverified regression point estimates remain pruned.

4. **Status of `revised_research_gap.md`:**
   - The obsolete v2.1 document has been **fully updated and superseded by v2.5** (`Reviewed v2.5`).
   - The ASCII prior-art table was purged of obsolete mismatched author names (Cui et al., Guo et al., Ren et al., Patel & Rao) and now accurately reflects the 17 verified included sources.
   - All text regarding John et al., Elia et al., and Saxena et al. explicitly reflects their Level 4 paywalled review status.

---

### 3.2 Exact Scenario Reporting & Cell Allocations

The pilot protocol partitions $N=60$ independent package journeys across 8 realistic logistics scenario types:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                PILOT SCENARIO ALLOCATION MATRIX (N = 60)                               │
├───────┬──────────────────────────────┬──────────┬───────────┬──────────────────────────┬───────────────┤
│ ID    │ Ground-Truth State (𝒢)       │ Journeys │ Cell Size │ Staged Physical Event    │ Target State  │
├───────┼──────────────────────────────┼──────────┼───────────┼──────────────────────────┼───────────────┤
│ SC-01 │ GT_INTACT (Standard)         │ J01–J15  │ n = 15    │ Package intact throughout│ OBS_DETERM    │
│ SC-02 │ GT_INTACT (Bag Change)       │ J16–J23  │ n = 8     │ Hub flyer bag replaced   │ OBS_DETERM    │
│ SC-03 │ GT_FORWARD_TRANSIT_DAMAGE    │ J24–J31  │ n = 8     │ Box crushed in transit   │ OBS_DETERM    │
│ SC-04 │ GT_DOORSTEP_SUBSTITUTION     │ J32–J39  │ n = 8     │ Cheaper unit substituted │ OBS_DETERM    │
│ SC-05 │ GT_CUSTOMER_TAMPER (Standard)│ J40–J47  │ n = 8     │ Customer dummy phone swap│ OBS_DETERM    │
│ SC-06 │ GT_REVERSE_TRANSIT_TAMPER    │ J48–J52  │ n = 5     │ Return bag slit/retaped  │ OBS_DETERM    │
│ SC-07 │ GT_CUSTOMER_TAMPER (Degraded)│ J53–J56  │ n = 4     │ Unreadable dark photos   │ OBS_DEGRADED  │
│ SC-08 │ GT_CUSTOMER_TAMPER (Ambiguou)│ J57–J60  │ n = 4     │ Screen scratch glare     │ OBS_INDIST    │
├───────┴──────────────────────────────┴──────────┼───────────┴──────────────────────────┴───────────────┤
│ TOTAL INDEPENDENT PACKAGE JOURNEYS              │ N = 60                                               │
└─────────────────────────────────────────────────┴──────────────────────────────────────────────────────┘
```

#### Denominators & Aggregation Rules:
- **Total Package Journeys:** $N = 60$.
- **Determinable Journeys:** $N_{\text{det}} = 15 + 8 + 8 + 8 + 8 + 5 = 52$ journeys.
- **Ambiguous / Degraded Journeys:** $N_{\text{ambig}} = 4 + 4 = 8$ journeys.
- **Determinable Discrepancy Journeys:** $N_{\text{discrepancy}} = 8 + 8 + 8 + 5 = 29$ journeys.
- **Intact Journeys:** $N_{\text{intact}} = 15 + 8 = 23$ journeys.
- **Cell Size Disclosure:** Discrepancy classes have cell sizes of **8, 8, 8, and 5**. No assertion of "eight journeys per class" is permitted.

---

### 3.3 Narrowed Research Claim: C-versus-D Treatment Definition

In earlier iterations, Condition D was described as testing "record linkage alone". However, Condition D introduces a richer multi-component user interface:
- **Condition C (Information-Matched Control):** Provides all 4 checkpoints ($CP_1, CP_2, CP_3, CP_4$) with identical 1080p images, identical 0.1g digital scale readings, courier scan logs, ISO-8601 timestamps, and **identical SHA-256 cryptographic verification stamps**. However, these records are presented in **four disconnected, unaligned tabs**. Reviewers must manually switch tabs, mentally calculate weight deltas, and visually inspect unaligned photos.
- **Condition D (Proposed Pipeline):** Presents the same evidence in a **unified chronological timeline** featuring:
  1. Automated side-by-side visual delta alignment ($CP_2$ forward delivery photos directly adjacent to $CP_3$ return pickup photos with synchronized pan and zoom);
  2. Continuous tare weight trajectory curves ($\Delta w = w_t - w_{\text{tare}}$) plotted across all 4 touchpoints; and
  3. Automated weight delta variance flags highlighting unexpected weight losses or gains.

#### Narrowed Research Claim:
> **Narrowed Research Question:**  
> *"Does a **combined linked-evidence presentation and automated visual/weight reconciliation pipeline** improve human adjudication decision accuracy, appropriate abstention, and operational policy alignment across the complete set of package journeys, compared to an unaligned, disconnected presentation of the identical underlying sensory evidence and cryptographic authenticity cues?"*

This narrower claim is methodologically defensible because it honestly reflects the multi-faceted intervention implemented in Condition D without claiming to isolate linkage from visual alignment or weight curve calculation.

---

### 3.4 Repaired Outcome Formulas & Coherent Evaluation Universe

#### The Evaluative Set Discordance & Condition-Specific Observability Problem:
If Condition D makes a journey determinable ($\Omega_{iD}^* = \text{OBS\_DETERMINABLE}$) that is ambiguous or indistinguishable under Condition C ($\Omega_{iC}^* \neq \text{OBS\_DETERMINABLE}$), calculating metrics conditional on a single static $\Omega_i^*$ distorts adjudication benchmarks. Furthermore, restricting metrics to determinable subsets evaluates Condition C and Condition D on **different subsets of journeys**, introducing severe selection bias.

#### Solution 1: Primary Evaluative Outcomes with Condition-Specific Observability ($\Omega_{ik}^*$) Across ALL 60 Journeys
1. **Overall Adjudication Accuracy ($OAA$):**
   Evaluates whether the reviewer renders the normatively correct decision on every journey $i \in \{1, \dots, 60\}$ given condition-specific observability $\Omega_{ik}^*$:
   $$Y_{ijk} = \begin{cases}
   1, & \text{if } \Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \text{Match}(\mathcal{A}_{ijk}, \mathcal{G}_i) \\
   1, & \text{if } \Omega_{ik}^* \neq \text{OBS\_DETERMINABLE} \land \mathcal{A}_{ijk} \in \{\text{ATTR\_ABSTAIN\_INDISTINGUISHABLE}, \text{ATTR\_ABSTAIN\_DEGRADED}\} \\
   0, & \text{otherwise}
   \end{cases}$$
   $$OAA_k = \frac{1}{60} \sum_{i=1}^{60} Y_{ijk}$$
   $OAA$ evaluates all four experimental conditions across the **exact same 60 journeys** ($N=60$). If a journey is ambiguous under Condition C ($\Omega_{iC}^* = \text{OBS\_INDISTINGUISHABLE}$), the optimal decision is appropriate abstention ($Y_{ijC} = 1$). If automated visual alignment under Condition D makes that same journey determinable ($\Omega_{iD}^* = \text{OBS\_DETERMINABLE}$), the optimal decision is correct attribution ($Y_{ijD} = 1$).

2. **Operational Decision Alignment ($ODA$):**
   Evaluates whether the platform's dispute resolution action $\mathcal{D}_{ijk}$ matches the condition-specific normative policy $\mathcal{D}_{ik}^* = \mathcal{D}^*(\mathcal{G}_i, \Omega_{ik}^*)$ across all 60 journeys:
   $$\mathcal{D}_{ik}^* = \mathcal{D}^*(\mathcal{G}_i, \Omega_{ik}^*) = \begin{cases}
   \text{DEC\_HOLD\_INVESTIGATION}, & \text{if } \Omega_{ik}^* \in \{\text{OBS\_INDISTINGUISHABLE}, \text{OBS\_DEGRADED\_INCOMPLETE}\} \\
   \text{DEC\_APPROVE\_REFUND}, & \text{if } \Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \mathcal{G}_i = \text{GT\_INTACT} \\
   \text{DEC\_CHARGEBACK\_CARRIER}, & \text{if } \Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \mathcal{G}_i \in \{\text{GT\_FWD\_TRANSIT\_DAMAGE}, \text{GT\_REV\_TRANSIT\_TAMPER}\} \\
   \text{DEC\_REJECT\_REFUND}, & \text{if } \Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \mathcal{G}_i \in \{\text{GT\_DOORSTEP\_SUBSTITUTION}, \text{GT\_CUSTOMER\_TAMPER}\}
   \end{cases}$$
   $$ODA_k = \frac{1}{60} \sum_{i=1}^{60} \mathbb{I}(\mathcal{D}_{ijk} = \mathcal{D}_{ik}^*)$$

#### Solution 2: Discrepancy Macro F1 as Secondary Metric with Coherent Universe
Macro F1 is retained as a secondary metric across the 4 physical discrepancy classes ($c \in \{1, 2, 3, 4\}$). To guarantee evaluation set coherence, $TP_c, FP_c, FN_c$ are defined over the **identical universe of all 60 journeys**:
$$\begin{aligned}
TP_c &= \sum_{i=1}^{60} \mathbb{I}(\mathcal{G}_i = g_c \land \mathcal{A}_{ijk} = a_c) \\
FP_c &= \sum_{i=1}^{60} \mathbb{I}(\mathcal{G}_i \neq g_c \land \mathcal{A}_{ijk} = a_c) \\
FN_c &= \sum_{i=1}^{60} \mathbb{I}(\mathcal{G}_i = g_c \land \mathcal{A}_{ijk} \neq a_c) \\
\text{Precision}_c &= \frac{TP_c}{TP_c + FP_c}, \quad \text{Recall}_c = \frac{TP_c}{TP_c + FN_c}, \quad F1_c = \frac{2 \cdot \text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c} \\
\text{Discrepancy Macro F1} &= \frac{1}{4} \sum_{c=1}^{4} F1_c
\end{aligned}$$

Because $TP, FP, FN$ sum over the identical set of 60 journeys:
- If a reviewer blames class $c$ on an intact journey or ambiguous journey, it is an $FP_c$.
- If a reviewer abstains or misidentifies class $c$, it is an $FN_c$.
- Denominators are mathematically coherent and non-contradictory.

---

### 3.5 Reassessed Statistical Model: Reviewer Fixed Effects

#### Instability of Random-Effect Estimators with $R=4$ Reviewers:
In standard mixed-effects modeling (e.g., `lme4` in R, `statsmodels` in Python), estimating a random-intercept variance component $\sigma_{\text{reviewer}}^2$ assumes that the sampled reviewers represent a random sample from a normal distribution $\mathcal{N}(0, \sigma^2)$. However:
1. $R=4$ levels of a grouping factor provide insufficient degrees of freedom to estimate a variance parameter reliably. Standard statistical guidelines recommend at least 10–20 clusters.
2. Optimization algorithms frequently produce singular fits ($\hat{\sigma}_{\text{reviewer}}^2 \approx 0$) or severe boundary errors, rendering random-effects estimates unstable and uninterpretable.

#### Adopted Statistical Specification (Reviewer Fixed Effects):
Reviewer heterogeneity is modeled via **fixed categorical indicator variables** (dummy variables $R_2, R_3, R_4$ taking $R_1$ as the reference baseline):

$$\text{logit}(P(Y_{ij} = 1)) = \beta_0 + \beta_B \cdot \text{Cond}_B + \beta_C \cdot \text{Cond}_C + \beta_D \cdot \text{Cond}_D + \sum_{r=2}^{4} \gamma_r \cdot \text{Reviewer}_{jr}$$

- **Advantage:** Directly controls for baseline differences in reviewer skill, conservatism, and calibration without requiring large-sample asymptotic assumptions on the rater distribution.
- **Clustering:** Journey-level clustering (repeated ratings of the same journey across conditions in the crossover Latin Square) is accounted for via **cluster-robust standard errors clustered at the journey level ($J_i$)**.
- **Primary Hypothesis Testing:**
  - Difference $\Delta OAA = OAA_{\text{Cond D}} - OAA_{\text{Cond C}}$ evaluated via **paired clustered bootstrap resampling ($B=2,000$ iterations)** clustered at the journey level.
  - Paired non-parametric permutation test (5,000 within-journey condition shuffles).
  - Paired exact McNemar's test for binary adjudication success $Y_{ij} \in \{0, 1\}$.

#### Limitations & Non-Generalizability:
- This is an **exploratory feasibility pilot** ($N=60$).
- Findings cannot be generalized to national e-commerce fraud prevalence rates, courier behavioral compliance, or platform-wide economic savings.

---

## 4. Structural Validation Report (Separately Reported)

In accordance with strict audit rules, **structural validation establishes only parsing and schema compliance, NOT factual accuracy or experimental authorization**:

- **Audited Files:**
  - `validated_closest_work_matrix.csv`: 17 data rows, 19 columns, 0 delimiter/trailing field errors.
  - `screening_ledger.csv`: 25 data rows (17 included + 6 full-text excluded + 2 unretrieved candidates), 15 columns, 0 delimiter errors.
  - `claim_evidence_ledger.csv`: 13 claim rows, 9 columns, 0 delimiter errors.
- **Structural Integrity Verdict:** **PASS (100% SCHEMA COMPLIANT)**.
- **Factual & Methodological Distinction:** Schema compliance does not clear readiness gates. Bibliographic verification and methodology checks remain separate.

---

## 5. Readiness Stage-Gate Status & Unresolved Issues

### 5.1 Pre-Experimental Readiness Gates (Physical Pilot Strictly Blocked)

| Pre-Experimental Gate ID | Requirement | Required Artifact | Status | Governance Ruling |
|:---:|---|---|:---:|:---:|
| **Gate E-1** | Protocol Freeze & Preregistration | Timestamped Git commit hash of Protocol v2.5.0 on public repository | **PENDING** | **BLOCKING EXPERIMENT** |
| **Gate E-2** | Ground-Truth Cryptography | Predeclared ground-truth ledger hash (SHA-256) committed to Git before staging | **PENDING** | **BLOCKING EXPERIMENT** |
| **Gate E-3** | Reviewer Calibration Trial | 10-case calibration trial completed with Reviewers $R_1, R_2, R_3, R_4$; baseline agreement $\kappa \ge 0.60$ documented | **PENDING** | **BLOCKING EXPERIMENT** |
| **Gate E-4** | Critical Prior-Art Clearance | Verified full-text review of Shiyamaladevi (2025) and Elia et al. (2024) confirming absence of multi-checkpoint linking | Level 5 (Mandatory Full Text) | **PENDING (NOT CLEARED)** | **BLOCKING EXPERIMENT** |

> [!CAUTION]
> **PHYSICAL EXPERIMENT STATUS: STRICTLY FROZEN.**  
> Gates E-1, E-2, E-3, and E-4 all remain **PENDING (NOT CLEARED)**. Specifically, Gate E-4 is not cleared because Elia et al. (2024) full text remains paywalled (HTTP 403 on Emerald Insight) and evaluated only at abstract and publisher summary level (Level 4). Research-gap assertions regarding Elia et al. remain strictly bounded to publisher case-study summaries and cannot be cited as fully established. Physical staging, courier photo captures, and human adjudication sessions remain **STRICTLY PROHIBITED** until all Pre-Experimental Gates (E-1 through E-4) are genuinely completed.

---

### 5.2 Pre-Publication Manuscript Gates (Required Before Paper Submission)

| Gate ID | Target Domain | Specific Gate Requirement | Current Status | Impact on Project |
|:---:|---|---|:---:|---|
| **Gate M-1** | Legal Citation Rigor | Procure certified primary orders for Adilabad (187/2025), Kurnool (18/2026), and Rangareddy (*T. Pranav Rao*) via eCourts India registry | **OPEN (SECONDARY REPORTING)** | Required for citing verbatim court holdings in manuscript. Does NOT block physical pilot. |
| **Gate M-2** | Search Rigor Export | Automated export receipts (`.bib` / `.csv` citation manifests) for Queries Q01, Q05, Q06 from institutional terminals | **OPEN (INTERACTIVE QUERY)** | Required for formal systematic review publication. Does NOT block physical pilot. |
| **Gate M-3** | Working Paper Verification | Procure complete manuscript of Bhattacharya (2026, SSRN 6803038) via interlibrary loan | **OPEN (ABSTRACT ONLY)** | Required before citing mathematical proofs. Does NOT block physical pilot. |
| **Gate M-4** | OR Conference Screen | Screen INFORMS, POMS, and SOM India (2023–2026) conference proceedings for adjacent reverse logistics papers | **OPEN (UNSCREENED)** | Required before making definitive literature gap assertions in journal submission. |

---

## 6. Audit Trail & File Modification Summary

The following files under `research/reviewed_v2/` have been updated and synchronized in this v2.5 release:

1. [`screening_ledger.csv`](research/reviewed_v2/screening_ledger.csv): Reconciled review levels for S02 (John et al.), S07 (Saxena et al.), and S09 (Elia et al.) to Level 4 (paywalled abstract / summary reviewed, `full_text_reviewed: NO`).
2. [`claim_evidence_ledger.csv`](research/reviewed_v2/claim_evidence_ledger.csv): Synchronized review levels for C01, C03, C04, C10; updated C12 to reflect 4 reviewers and exact scenario counts (8, 8, 8, 5; 15, 8; 4, 4; total 60).
3. [`search_reconciliation.md`](research/reviewed_v2/search_reconciliation.md): Clarified peer-reviewed journal article review tiers in Table §4 disaggregating full-text reviewed works from paywalled abstract/summary-reviewed sources.
4. [`revised_research_gap.md`](research/reviewed_v2/revised_research_gap.md): Updated from v2.1 to v2.5; replaced obsolete mismatched citation names with authentic 17 sources; harmonized John, Elia, Saxena review levels; narrowed research gap to combined linked-presentation and automated reconciliation intervention; updated Gate E-3 to 4 reviewers.
5. [`revised_experiment_protocol.md`](research/reviewed_v2/revised_experiment_protocol.md): Updated to v2.5.0; narrowed C vs D research claim; enforced exact scenario cell sizes (8, 8, 8, 5); defined primary outcomes ($OAA$ and $ODA$) across all 60 journeys; repaired Discrepancy Macro F1 formulas with coherent 60-journey evaluation set; replaced unstable GLMM random rater effects with Reviewer Fixed Effects in logistic regression; documented uncertainty analysis and disclaimed national generalizability.
6. [`decision_and_unresolved_gates.md`](research/reviewed_v2/decision_and_unresolved_gates.md): Updated to v2.5; aligned protocol version references to v2.5.0; confirmed that physical experiment remains strictly blocked pending Gates E-1, E-2, E-3, and E-4.
7. [`final_correction_report_v2.5.md`](research/reviewed_v2/final_correction_report_v2.5.md): This comprehensive defect closure report.

---

## 7. Mandatory Governance Conclusion

The protocol and supporting evidence artifacts in `research/reviewed_v2/` are now internally coherent, mathematically sound, bibliographically synchronized, and statistically defensible. 

However, in accordance with scientific governance rules:
- **Structural and parsing validity does not equal experimental authorization.**
- **The Phase 1 physical experiment remains STRICTLY BLOCKED / FROZEN.**
- **Gate E-4 is PENDING (NOT CLEARED)** because Elia et al. (2024) full text is paywalled.
- Physical packaging, courier staging, and human adjudication sessions will not proceed until Pre-Execution Readiness Gates E-1, E-2, E-3, and E-4 are genuinely completed and cryptographically verified.
