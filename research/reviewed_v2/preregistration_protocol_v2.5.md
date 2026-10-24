# TriNetra AI: Pre-Registration Protocol (Reviewed v2.5)

> **Document Type:** Formal Open Science Framework (OSF) Pre-Registration Specification  
> **Protocol Version:** 2.5.0  
> **Date of Preparation:** 2026-10-24  
> **Study Classification:** Exploratory Feasibility Pilot ($N=60$ Independent Package Journeys)  
> **Pre-Registration Status:** PENDING CRYPTOGRAPHIC COMMITMENT (Execution Frozen)  
> **Associated Repositories:** `TriNetra_Mobile/research/reviewed_v2/`  

---

## 1. Study Information

### 1.1 Study Title
Evaluating Multi-Checkpoint Visual and Tare Weight Evidence Linkage for Reverse Logistics E-Commerce Return Fraud Adjudication: An Exploratory Feasibility Pilot.

### 1.2 Research Questions
1. **Primary Question (Combined Linked-Presentation & Automated Reconciliation Intervention):**  
   Does providing human adjudicators with a **combined linked-evidence presentation and automated visual/weight reconciliation pipeline** (chronological timeline, aligned side-by-side visual comparison, continuous tare weight curves, and variance anomaly flags) improve Overall Adjudication Accuracy ($OAA$), Operational Decision Alignment ($ODA$), and appropriate abstention across 60 package journeys, compared to an **information-matched disconnected control** (Condition C) providing the identical underlying photographs, scale readings, and SHA-256 cryptographic authenticity badges in an unaligned four-tab interface?
2. **Secondary Question (Evidence Availability):**  
   What is the incremental adjudication benefit of multi-checkpoint visual and weight evidence (Conditions C and D, four checkpoints) compared to isolated single-point warehouse receiving (Condition A, $CP_4$ only) and disconnected two-point endpoints (Condition B, $CP_1$ and $CP_4$)?

### 1.3 Hypotheses
- **Hypothesis 1 (Primary - $OAA$):**  
  Human adjudicators evaluating package journeys under Condition D will achieve higher Overall Adjudication Accuracy than under Condition C:  
  $$H_{10}: OAA_{\text{Cond D}} \le OAA_{\text{Cond C}} \quad \text{vs.} \quad H_{1A}: OAA_{\text{Cond D}} > OAA_{\text{Cond C}}$$
- **Hypothesis 2 (Primary - $ODA$):**  
  Platform operational business decisions rendered under Condition D will achieve higher alignment with normative business policy than under Condition C:  
  $$H_{20}: ODA_{\text{Cond D}} \le ODA_{\text{Cond C}} \quad \text{vs.} \quad H_{2A}: ODA_{\text{Cond D}} > ODA_{\text{Cond C}}$$
- **Hypothesis 3 (Secondary - Discrepancy Macro F1):**  
  Condition D will yield a superior Macro-averaged F1 score across the four physical handover discrepancy categories (`GT_FORWARD_TRANSIT_DAMAGE`, `GT_DOORSTEP_SUBSTITUTION`, `GT_CUSTOMER_TAMPER`, `GT_REVERSE_TRANSIT_TAMPER`) evaluated over all 60 journeys compared to Condition C:  
  $$H_{30}: \text{Macro F1}_{\text{Cond D}} \le \text{Macro F1}_{\text{Cond C}} \quad \text{vs.} \quad H_{3A}: \text{Macro F1}_{\text{Cond D}} > \text{Macro F1}_{\text{Cond C}}$$
- **Hypothesis 4 (Secondary - Appropriate Abstention):**  
  On observationally indistinguishable or sensor-degraded package journeys ($n=8$, $J_{53}-J_{60}$), Condition D will exhibit a higher Appropriate Abstention Rate ($AAR$) and lower Unsupported Blame Rate ($UBR$) than Condition C.
- **Hypothesis 5 (Secondary - Reviewer Latency):**  
  Adjudication duration per case will be significantly lower under Condition D than under Condition C due to automated visual alignment and tare curve calculation.

---

## 2. Sampling & Staging Plan

### 2.1 Sample Size
- **Total Package Journeys:** Exactly $N=60$ physical package journeys.
- **Total Observations:** $4 \times 60 = 240$ human adjudication ratings generated across a $4 \times 4$ balanced Latin Square crossover design (4 human reviewers $\times$ 60 unique cases).
- **Physical Sensing Boundary:** Each package is tracked across four physical logistics checkpoints:
  1. Checkpoint 1 ($CP_1$): Seller / Hub Dispatch
  2. Checkpoint 2 ($CP_2$): Forward Doorstep Open Box Delivery (OBD)
  3. Checkpoint 3 ($CP_3$): Reverse Return Pickup Handover
  4. Checkpoint 4 ($CP_4$): Reverse Fulfillment Warehouse Receiving

### 2.2 Scenario Cell Allocations ($N=60$)
The 60 journeys are partitioned into 8 specific scenario cells with exact sample sizes:

| Scenario ID | Ground-Truth State ($\mathcal{G}_i$) | Sample Size ($n$) | Journey IDs | Staged Physical Condition |
|:---:|---|:---:|:---:|---|
| **SC-01** | `GT_INTACT` (Standard Intact) | 15 | $J_{01} - J_{15}$ | Item, box, seals, and weight intact and unchanged across all 4 checkpoints. |
| **SC-02** | `GT_INTACT` (Permitted Bag Change) | 8 | $J_{16} - J_{23}$ | Outer flyer bag replaced at carrier transit hub with carrier scan log; primary box intact. |
| **SC-03** | `GT_FORWARD_TRANSIT_DAMAGE` | 8 | $J_{24} - J_{31}$ | Primary box crushed/creased between $CP_1$ dispatch and $CP_2$ delivery; seal unbroken. |
| **SC-04** | `GT_DOORSTEP_SUBSTITUTION` | 8 | $J_{32} - J_{39}$ | High-value phone swapped for lower-tier model at delivery handover $CP_2$ (replicates *Adilabad* case). |
| **SC-05** | `GT_CUSTOMER_TAMPER` | 8 | $J_{40} - J_{47}$ | Customer replaces genuine phone with dummy unit / weight insert during custody ($CP_2 \to CP_3$). |
| **SC-06** | `GT_REVERSE_TRANSIT_TAMPER` | 5 | $J_{48} - J_{52}$ | Return flyer slit and retaped during reverse transit ($CP_3 \to CP_4$); phone extracted. |
| **SC-07** | `GT_CUSTOMER_TAMPER` (Degraded) | 4 | $J_{53} - J_{56}$ | Customer tamper staged, but $CP_3$ capture suffers dark lighting ($<15\text{ lux}$) and 0.0g scale error. |
| **SC-08** | `GT_CUSTOMER_TAMPER` (Ambiguous) | 4 | $J_{57} - J_{60}$ | Fine hairline screen scratch staged; specular glare obscures defect region at both $CP_2$ and $CP_3$. |
| **TOTAL** | — | **60** | $J_{01} - J_{60}$ | **52 determinable journeys, 8 degraded/ambiguous journeys.** |

*(Note: Cell counts are strictly 8, 8, 8, and 5 for the 4 discrepancy classes; exactly 23 intact journeys; 8 degraded/ambiguous journeys. Total = 60).*

### 2.3 Exclusions from Primary Estimand
- `GT_VENDOR_DEFECT` (Latent manufacturing defect originating before seller dispatch; unobservable at $CP_1$ without unboxing).
- `GT_WAREHOUSE_HANDLING_DAMAGE` (Damage occurring inside warehouse sortation after intake $CP_4$; requires internal facility CCTV).
Both classes are formally designated outside the Phase 1 pilot estimand.

---

## 3. Experimental Design & Latin Square Crossover

### 3.1 Experimental Conditions
All conditions present evidence collected from the same physical package journeys:

1. **Condition A (Baseline 0 - Isolated Warehouse Receiving):**  
   Presents Checkpoint 4 ($CP_4$) data only (receiving photo, receiving scale weight, timestamp, single-record SHA-256 stamp).
2. **Condition B (Baseline 1 - Disconnected Two-Point):**  
   Presents Checkpoint 1 ($CP_1$) and Checkpoint 4 ($CP_4$) in separate unaligned tabs with endpoint SHA-256 stamps.
3. **Condition C (Baseline 2 - Information-Matched Control):**  
   Presents all four checkpoints ($CP_1, CP_2, CP_3, CP_4$) in four separate unaligned tabs. Reviewers must manually switch tabs, manually inspect unaligned photos, and mentally calculate weight deltas. Displays identical SHA-256 verification badges on all four records.
4. **Condition D (Proposed Intervention Pipeline):**  
   Presents all four checkpoints in a unified chronological interface featuring automated side-by-side visual delta comparison ($CP_2$ delivery photo aligned with $CP_3$ pickup photo with synchronized pan/zoom), automated continuous tare weight curves ($\Delta w = w_t - w_{\text{tare}}$), automated weight anomaly flags, and identical SHA-256 verification badges on all four records.

### 3.2 Latin Square Crossover Allocation
Four human reviewers ($R_1, R_2, R_3, R_4$) evaluate the 60 journeys across four 15-case blocks with a 48-hour washout period between blocks. Each reviewer evaluates each physical journey exactly once:

| Session / Block | Journey Range | Reviewer 1 ($R_1$) | Reviewer 2 ($R_2$) | Reviewer 3 ($R_3$) | Reviewer 4 ($R_4$) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **Block 1** | $J_{01} - J_{15}$ | Condition A | Condition B | Condition C | Condition D |
| *Washout* | — | *48 hours* | *48 hours* | *48 hours* | *48 hours* |
| **Block 2** | $J_{16} - J_{30}$ | Condition B | Condition C | Condition D | Condition A |
| *Washout* | — | *48 hours* | *48 hours* | *48 hours* | *48 hours* |
| **Block 3** | $J_{31} - J_{45}$ | Condition C | Condition D | Condition A | Condition B |
| *Washout* | — | *48 hours* | *48 hours* | *48 hours* | *48 hours* |
| **Block 4** | $J_{46} - J_{60}$ | Condition D | Condition A | Condition B | Condition C |

- Case order is independently randomized within each 15-case block.
- Condition names are masked from reviewers ("Case Evaluation Session").
- **Case Tracking ID Anonymization & Ground-Truth Blinding:** Sequential Journey IDs ($J_{01}-J_{60}$) are internal physical staging indices and are strictly withheld from reviewers. In all evaluation sessions, cases are presented under randomized, blinded Tracking Codes (`CASE-XXXX`) generated via a confidential random permutation table held exclusively by the trial coordinator. The plaintext truth ledger is embargoed until all 240 evaluations are completed, preventing reviewers from linking case codes to scenario groups.
- **Pre-Trial Interface Familiarization:** Following Gate E-3 clearance and prior to Session 1, reviewers complete a separate, unscored tool orientation using 2–3 dummy non-experimental cases (`ORIENT-01`, `ORIENT-02`). The 60 experimental package journeys ($J_{01}-J_{60}$) are strictly prohibited from practice.
- Maximum time budget per case: 3.0 minutes (180 seconds).

---

## 4. Objective, Evidence-Based Observability Criteria ($\Omega_{ik}^*$)

### 4.1 Strict Conceptual Separation
Observability $\Omega_{ik}^* \in \{\text{OBS\_DETERMINABLE}, \text{OBS\_INDISTINGUISHABLE}, \text{OBS\_DEGRADED\_INCOMPLETE}\}$ represents the **epistemological deduicibility of the physical origin stage under the data mask of condition $k$ by an ideal observer**. It is NOT a measure of human rater fatigue or UI convenience.

### 4.2 Mathematical Rules for Observability State Assignment

#### Rule 1: Transition Isolation (Determinability)
A discrepancy occurring during transition $\tau = (CP_{\text{start}} \to CP_{\text{end}})$ is `OBS_DETERMINABLE` under condition mask $M_k$ if and only if:
1. $CP_{\text{start}} \in M_k$ and $CP_{\text{end}} \in M_k$.
2. The physical sensory capture at $CP_{\text{start}}$ proves intact state: visual seal intact, no carton crush, and measured weight $w_{\text{start}} \in [w_{\text{nom}} - 1.0\text{g}, w_{\text{nom}} + 1.0\text{g}]$.
3. The physical sensory capture at $CP_{\text{end}}$ proves anomaly: visible structural carton crease/tear, broken factory seal, mismatched model barcode, or measured weight step-change $|\Delta w| > 2.0\text{g}$.
4. Data quality criteria are met: image resolution $\ge 1080\text{p}$, illuminance $\ge 150\text{ lux}$, absence of obscuring glare/shadow over the defect area, and scale calibration uncertainty $\le \pm 0.1\text{g}$.

#### Rule 2: Mask Incompleteness (Interval Indistinguishability)
If an anomaly is documented at $CP_{\text{later}} \in M_k$, but one or more intervening handover checkpoints $CP_{\text{intervening}} \notin M_k$, the transition stage is physically unisolated:
- Under Condition A ($CP_4$ only): SC-02, SC-03, SC-04, SC-05, SC-06 lack $CP_1, CP_2, CP_3$. An observer cannot establish whether the defect occurred in forward transit, delivery, consumer custody, or reverse transit. Therefore, $\Omega_{iA}^* = \text{OBS\_INDISTINGUISHABLE}$. (For SC-01, where factory seal and weight match specification at $CP_4$, intact status is verified: $\Omega_{iA}^* = \text{OBS\_DETERMINABLE}$).
- Under Condition B ($CP_1, CP_4$): SC-02, SC-03, SC-04, SC-05, SC-06 lack intermediate handovers $CP_2$ and $CP_3$. An observer cannot determine whether a transition occurred before, during, or after customer custody. Therefore, $\Omega_{iB}^* = \text{OBS\_INDISTINGUISHABLE}$. (For SC-01, endpoints match: $\Omega_{iB}^* = \text{OBS\_DETERMINABLE}$).

#### Rule 3: Sensory Degradation
If a checkpoint within the candidate transition interval suffers corrupted or incomplete sensory acquisition:
- Image illuminance $< 15\text{ lux}$, motion blur (Laplacian variance $< 100$), critical occlusion, or scale measurement failure ($0.0\text{g}$ / missing).
- Then $\Omega_{ik}^* = \text{OBS\_DEGRADED\_INCOMPLETE}$. (Applies to SC-07, $J_{53}-J_{56}$ across all conditions).

#### Rule 4: Ambiguity Under Glare / Specular Reflection
If photographic evidence at candidate transition boundaries suffers specular glare obscuring the micro-defect region, such that the image is equally consistent with intactness and damage:
- Then $\Omega_{ik}^* = \text{OBS\_INDISTINGUISHABLE}$. (Applies to SC-08, $J_{57}-J_{60}$ across all conditions).

#### Rule 5: Symmetrical Sensory Equivalence Between Condition C and Condition D
Because Condition C and Condition D provide **identical underlying photographs, scale readings, courier scan notes, and SHA-256 verification stamps across all four checkpoints** ($M_C = M_D = \{CP_1, CP_2, CP_3, CP_4\}$):
- The objective physical evidence accessible in the data mask is **identical**.
- Therefore, **$\Omega_{iC}^* = \Omega_{iD}^*$ for all 60 journeys ($i=1, \dots, 60$)**.
- Condition C is NOT arbitrarily classified as ambiguous simply because its UI is unaligned. Both conditions are objectively determinable on $J_{01}-J_{52}$ and objectively non-determinable on $J_{53}-J_{60}$.
- The experimental test is whether Condition D's automated visual delta alignment and continuous tare curves enable **human adjudicators** to correctly identify the objective truth more reliably than Condition C's manual interface.

---

## 5. Variables & Mathematical Formulations

### 5.1 Measured Variables
- **Reviewer Attribution ($\mathcal{A}_{ijk}$):** Standardized dropdown selection:
  `ATTR_CONFIRMED_LEGITIMATE`, `ATTR_STAGE_FORWARD_TRANSIT`, `ATTR_STAGE_DOORSTEP_DELIVERY`, `ATTR_STAGE_CONSUMER_CUSTODY`, `ATTR_STAGE_REVERSE_TRANSIT`, `ATTR_STAGE_OTHER_OUTSIDE_SCOPE`, `ATTR_ABSTAIN_INDISTINGUISHABLE`, `ATTR_ABSTAIN_DEGRADED`.
- **Operational Decision ($\mathcal{D}_{ijk}$):** Standardized dropdown selection:
  `DEC_APPROVE_REFUND`, `DEC_REJECT_REFUND`, `DEC_HOLD_INVESTIGATION`, `DEC_CHARGEBACK_CARRIER`, `DEC_CHARGEBACK_VENDOR`.
- **Reviewer Latency ($T_{ijk}$):** Duration from case load to form submission (seconds).

### 5.2 Primary Outcomes (Common Set of All 60 Journeys)

#### 1. Overall Adjudication Accuracy ($OAA$)
Scored across all 60 journeys against condition-specific normative standard $\Omega_{ik}^*$:
$$Y_{ijk} = \begin{cases}
1, & \text{if } (\Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \text{Match}(\mathcal{A}_{ijk}, \mathcal{G}_i)) \lor (\Omega_{ik}^* \neq \text{OBS\_DETERMINABLE} \land \mathcal{A}_{ijk} \in \{\text{ATTR\_ABSTAIN\_*}\}) \\
0, & \text{otherwise}
\end{cases}$$

$$OAA_k = \frac{1}{60} \sum_{i=1}^{60} Y_{ijk}$$

#### 2. Operational Decision Alignment ($ODA$)
$$ODA_k = \frac{1}{60} \sum_{i=1}^{60} \mathbb{I}(\mathcal{D}_{ijk} = \mathcal{D}_{ik}^*)$$
Where $\mathcal{D}_{ik}^* = \mathcal{D}^*(\mathcal{G}_i, \Omega_{ik}^*)$ is the normative business policy:
- `DEC_HOLD_INVESTIGATION` if $\Omega_{ik}^* \neq \text{OBS\_DETERMINABLE}$.
- `DEC_APPROVE_REFUND` if $\Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \mathcal{G}_i = \text{GT\_INTACT}$.
- `DEC_CHARGEBACK_CARRIER` if $\Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \mathcal{G}_i \in \{\text{GT\_FWD\_TRANSIT\_DAMAGE}, \text{GT\_REV\_TRANSIT\_TAMPER}\}$.
- `DEC_REJECT_REFUND` if $\Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \mathcal{G}_i \in \{\text{GT\_DOORSTEP\_SUBSTITUTION}, \text{GT\_CUSTOMER\_TAMPER}\}$.

### 5.3 Secondary Outcomes
- **Discrepancy Macro F1:** Evaluated across the 4 physical discrepancy classes over all 60 journeys ($TP_c, FP_c, FN_c$ defined over $i \in \{1,\dots,60\}$).
- **Appropriate Abstention Rate ($AAR_k$):** $\frac{1}{|\mathcal{N}_{\text{ambig},k}|} \sum_{i \in \mathcal{N}_{\text{ambig},k}} \mathbb{I}(\mathcal{A}_{ijk} \in \{\text{ATTR\_ABSTAIN\_*}\} )$.
- **Unsupported Blame Rate ($UBR_k$):** $\frac{1}{|\mathcal{N}_{\text{ambig},k}|} \sum_{i \in \mathcal{N}_{\text{ambig},k}} \mathbb{I}(\mathcal{A}_{ijk} \in \{\text{ATTR\_STAGE\_*}\} )$.
- **Unnecessary Abstention Rate ($UAR_k$):** $\frac{1}{|\mathcal{N}_{\text{det},k}|} \sum_{i \in \mathcal{N}_{\text{det},k}} \mathbb{I}(\mathcal{A}_{ijk} \in \{\text{ATTR\_ABSTAIN\_*}\} )$.
- **Reviewer Time-to-Decision:** Mean latency in seconds.

---

## 6. Statistical Analysis Plan

### 6.1 Primary Hypothesis Testing ($H_1: OAA_{\text{Cond D}} > OAA_{\text{Cond C}}$)
1. **Journey-Clustered Bootstrap ($B=2,000$ iterations):**
   - Resample 60 package journeys with replacement, preserving within-journey paired structure across conditions.
   - Compute $\Delta OAA^{(b)} = OAA_{\text{Cond D}}^{(b)} - OAA_{\text{Cond C}}^{(b)}$.
   - Calculate 95% percentile confidence interval $[\Delta OAA_{2.5\%}, \Delta OAA_{97.5\%}]$. Reject null if lower bound $> 0$.
2. **Paired Permutation Test (5,000 permutations):**
   - Randomly flip condition labels (Condition C vs Condition D) within each journey with probability 0.5.
   - Compute empirical two-sided permutation $p$-value. Threshold: $\alpha = 0.05$.
3. **McNemar's Exact Paired Test:**
   - Evaluated on paired binary outcomes $Y_{i, \text{Cond C}}$ vs $Y_{i, \text{Cond D}}$ for discordant pairs.

### 6.2 Reviewer Fixed Effects Regression Model
To account for individual reviewer variation across the $R=4$ human evaluators without imposing unstable random-effects variance estimation on small cluster counts:

$$\text{logit}(P(Y_{ij} = 1)) = \beta_0 + \beta_B \cdot \text{Cond}_B + \beta_C \cdot \text{Cond}_C + \beta_D \cdot \text{Cond}_D + \sum_{r=2}^{4} \gamma_r \cdot \text{Reviewer}_{jr}$$

- Reference condition: Condition A.
- Primary treatment contrast of interest: $\Delta \beta = \beta_D - \beta_C$ (evaluated via Wald test with cluster-robust standard errors clustered at package journey level $J_i$).

---

## 7. Pre-Execution Gate Requirements (Study Execution Gated)

Experimental execution is strictly gated until Pre-Execution Gates E-1, E-2, and E-3 are satisfied:

| Gate ID | Requirement | Target Criterion | Pre-Registration Status |
|:---:|---|---|:---:|
| **Gate E-1** | Protocol Freeze & Preregistration | Timestamped Git commit hash on public repository | **PENDING (Awaiting Lead Approval)** |
| **Gate E-2** | Truth Ledger Hash Pre-Commitment | SHA-256 hash manifest committed to Git before staging (plaintext ledger embargoed for blinding) | **PENDING (Awaiting Lead Approval)** |
| **Gate E-3** | Reviewer Calibration Trial | 10-case text-based rubric calibration across four real independent Reviewers $R_1-R_4$ with Fleiss' $\kappa \ge 0.60$; separate unscored UI familiarization | **PENDING (Awaiting 4 Real Reviewers)** |

> [!NOTE]
> **Prior-Art Full-Text Clearance (Gate M-5):** Full-text procurement and review of Elia et al. (2024, Emerald Insight) is formally designated as **Pre-Publication Gate M-5** (literature clearance prior to final manuscript submission). In accordance with Level 4 abstract/case-summary review, novelty claims remain strictly bounded to exploratory feasibility. It does NOT block physical packaging or reviewer adjudication. Physical execution will commence once Gates E-1, E-2, and E-3 are completed.
