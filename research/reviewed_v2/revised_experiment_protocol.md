# Revised Phase 1 Experimental Research Protocol (Reviewed v2.5)

> **Protocol Version:** 2.5.0 (Targeted Protocol, Formula, & Statistical Model Corrections)  
> **Document Type:** Pre-Registration Experimental Research Protocol  
> **Date:** 2026-10-24  
> **Reviewer Role:** Independent Senior Research-Methodology Reviewer  
> **Study Status:** GATED — Execution Frozen Pending Pre-Execution Gates E-1 through E-4  
> **Classification:** Exploratory Feasibility Pilot ($N=60$ Independent Package Journeys)  

---

## 1. Primary Research Question, Scope Boundary, & Estimand

### 1.1 Primary Research Question
Does providing a **combined linked-evidence presentation and automated visual/weight reconciliation pipeline** (chronological timeline, aligned side-by-side visual comparison, continuous tare weight curves, and variance anomaly flags) improve adjudication accuracy, appropriate abstention, and operational decision alignment across the complete set of package journeys, compared to:
1. **Isolated single-point and disconnected two-point baselines** (Conditions A and B, measuring the effect of evidence availability); and
2. **A disconnected multi-point baseline with identical underlying evidence and identical cryptographic authenticity cues** (Condition C, measuring the isolated effect of the combined linked-presentation and automated-reconciliation intervention holding information content and perceived authenticity constant)?

### 1.2 Defining the Pilot Estimand & Taxonomic Trade-Off Analysis
In an exploratory pilot restricted to $N=60$ independent package journeys, there is a fundamental methodological trade-off between broad taxonomic coverage and cell-level statistical power:
- **Trade-Off Analysis:** Attempting to evaluate six discrepancy categories plus legitimate intact cases, sensor-degraded cases, and observationally indistinguishable cases across $N=60$ would reduce cell sizes to $n \le 4$ per category. This would introduce extreme sampling variance into class-specific F1 scores and render statistical inference meaningless.
- **Physical Sensing Boundary:** TriNetra's sensing envelope directly captures the **four physical handover transitions** connecting dispatch, delivery, and return:
  - Checkpoint 1 ($CP_1$): Hub / Seller Dispatch
  - Checkpoint 2 ($CP_2$): Forward Doorstep Open Box Delivery (OBD)
  - Checkpoint 3 ($CP_3$): Reverse Return Pickup Handover
  - Checkpoint 4 ($CP_4$): Reverse Fulfillment Warehouse Receiving
- **Estimand Specification & Cell Counts:** The primary evaluative estimand is strictly bounded to the **four physical discrepancy transition stages** occurring across these checkpoints, staged with exact cell allocations:
  1. `GT_FORWARD_TRANSIT_DAMAGE` ($n=8$, $J_{24}-J_{31}$: damage incurred between $CP_1$ dispatch and $CP_2$ delivery);
  2. `GT_DOORSTEP_SUBSTITUTION` ($n=8$, $J_{32}-J_{39}$: item substituted at forward delivery handover $CP_2$);
  3. `GT_CUSTOMER_TAMPER` ($n=8$, $J_{40}-J_{47}$: tampering/swap occurring during consumer custody between $CP_2$ and $CP_3$);
  4. `GT_REVERSE_TRANSIT_TAMPER` ($n=5$, $J_{48}-J_{52}$: tampering/theft incurred in reverse transit between $CP_3$ and $CP_4$).
  *(Note: Cell sizes are exactly 8, 8, 8, and 5; we do NOT claim eight journeys per class).*
- **Additional Evaluated Scenario Groups:**
  - `GT_INTACT`: Standard intact ($n=15$, $J_{01}-J_{15}$) and permitted bag-change intact ($n=8$, $J_{16}-J_{23}$); total intact journeys = 23.
  - Sensor-Degraded Tampering: ($n=4$, $J_{53}-J_{56}$).
  - Ambiguous / Indistinguishable Tampering: ($n=4$, $J_{57}-J_{60}$).
  - Total Pilot Sample Size: Exactly $N=60$ independent package journeys (52 determinable, 8 degraded/ambiguous).
- **Explicit Scope Exclusions from Primary Estimand:**
  - `GT_VENDOR_DEFECT` (Latent manufacturing defect originating before seller dispatch inside factory-sealed packaging; unobservable at $CP_1$ without unboxing);
  - `GT_WAREHOUSE_HANDLING_DAMAGE` (Damage occurring inside fulfillment center sortation after receiving intake $CP_4$; requires internal facility CCTV rather than transport handover inspection).
  These two classes are formally designated **outside the Phase 1 pilot estimand**, ensuring that physical staging focuses with high fidelity on the reverse-logistics handover transitions TriNetra is designed to solve.

### 1.3 Predefined Primary Outcomes (Evaluated Across All 60 Journeys)
1. **Overall Adjudication Accuracy ($OAA$):** Proportion of all $N=60$ package journeys where the reviewer renders the correct evaluative decision given ground truth and condition-specific observability: correct stage/intact attribution on condition-determinable journeys ($\Omega_{ik}^* = \text{OBS\_DETERMINABLE}$), and appropriate abstention on condition-ambiguous or degraded journeys ($\Omega_{ik}^* \neq \text{OBS\_DETERMINABLE}$). Evaluated over the identical 60 journeys across all conditions.
2. **Operational Decision Alignment ($ODA$):** Proportion of all $N=60$ package journeys where the reviewer's platform action matches the condition-specific normative business policy $\mathcal{D}_{ik}^* = \mathcal{D}^*(\mathcal{G}_i, \Omega_{ik}^*)$.

### 1.4 Predefined Secondary Outcomes
1. **Discrepancy Macro F1 (Conditional Secondary Metric):** Macro-averaged F1 score calculated across the four physical handover discrepancy categories (`GT_FORWARD_TRANSIT_DAMAGE`, `GT_DOORSTEP_SUBSTITUTION`, `GT_CUSTOMER_TAMPER`, `GT_REVERSE_TRANSIT_TAMPER`) with True Positives, False Positives, and False Negatives defined over the coherent universe of all 60 journeys.
2. **Appropriate Abstention Rate ($AAR$):** The proportion of observationally indistinguishable or degraded cases ($n=8$, $J_{53}-J_{60}$) where the reviewer correctly abstains from assigning unsupported blame (`ATTR_ABSTAIN_INDISTINGUISHABLE` or `ATTR_ABSTAIN_DEGRADED`).
3. **Unsupported Blame Rate ($UBR$):** Proportion of observationally indistinguishable or degraded cases ($n=8$, $J_{53}-J_{60}$) where a reviewer assigns blame to a specific logistics actor or stage despite insufficient evidence.
4. **Unnecessary Abstention Rate ($UAR$):** Proportion of determinable cases ($n=52$, $J_{01}-J_{52}$) where physical evidence objectively establishes the origin stage, but the reviewer unnecessarily declines attribution.
5. **Reviewer Time-to-Decision:** Mean adjudication duration per case (seconds) across experimental conditions.

---

## 2. Strict Conceptual Layer Separation & Dedicated Vocabularies

To eliminate epistemological conflation, this protocol enforces distinct, non-overlapping vocabularies across all five conceptual layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│ [LAYER 1] PHYSICAL GROUND TRUTH (𝒢)                                    │
│ Physical reality established a priori in the staged package:           │
│ • GT_INTACT (Legitimate item, intact across all checkpoints)           │
│ • GT_FORWARD_TRANSIT_DAMAGE (Crushed/creased between CP₁ and CP₂)       │
│ • GT_DOORSTEP_SUBSTITUTION (Substituted at forward delivery CP₂)       │
│ • GT_CUSTOMER_TAMPER (Altered/swapped during consumer custody)         │
│ • GT_REVERSE_TRANSIT_TAMPER (Slit/retaped between CP₃ and CP₄)         │
│ [EXCLUDED FROM PILOT ESTIMAND: GT_VENDOR_DEFECT, GT_WH_HANDLING_DMG]   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Sensor Capture / Masking
┌──────────────────────────────────▼─────────────────────────────────────┐
│ [LAYER 2] PHYSICAL OBSERVATIONS (𝒪)                                    │
│ Raw sensory captures: Images I₁, I₂, I₃, I₄; Scale weights w₁, w₂, w₃, │
│ w₄; Barcode scans, timestamps, courier inspection notes.               │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Epistemological Deduction
┌──────────────────────────────────▼─────────────────────────────────────┐
│ [LAYER 3] OBSERVABILITY STATE (Ω)                                      │
│ Condition-specific deductive capacity under the active evidence mask:  │
│ • OBS_DETERMINABLE: Evidence objectively proves exact stage origin.    │
│ • OBS_INDISTINGUISHABLE: Evidence equally consistent with ≥2 stages.   │
│ • OBS_DEGRADED_INCOMPLETE: Sensor data missing, blurry, or occluded.   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Human Evaluative Judgment
┌──────────────────────────────────▼─────────────────────────────────────┐
│ [LAYER 4] REVIEWER ATTRIBUTION ASSESSMENT (𝒜)                         │
│ Standardized options presented in reviewer evaluation dropdown:        │
│ • ATTR_CONFIRMED_LEGITIMATE (Confirms package intact, no foul play)    │
│ • ATTR_STAGE_FORWARD_TRANSIT (Blames forward carrier transit)          │
│ • ATTR_STAGE_DOORSTEP_DELIVERY (Blames forward delivery handover)      │
│ • ATTR_STAGE_CONSUMER_CUSTODY (Blames consumer tampering/swap)         │
│ • ATTR_STAGE_REVERSE_TRANSIT (Blames reverse return carrier transit)   │
│ • ATTR_STAGE_OTHER_OUTSIDE_SCOPE (Blames upstream/downstream stage)    │
│ • ATTR_ABSTAIN_INDISTINGUISHABLE (Declines to blame; ambiguous facts)  │
│ • ATTR_ABSTAIN_DEGRADED (Declines to blame; insufficient/dark photos)  │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Automated / Business Policy
┌──────────────────────────────────▼─────────────────────────────────────┐
│ [LAYER 5] OPERATIONAL DECISION (𝒟)                                     │
│ Business execution executed by platform:                               │
│ • DEC_APPROVE_REFUND                                                   │
│ • DEC_REJECT_REFUND                                                    │
│ • DEC_HOLD_INVESTIGATION                                               │
│ • DEC_CHARGEBACK_CARRIER                                               │
│ • DEC_CHARGEBACK_VENDOR                                                │
└────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> `OBS_INDISTINGUISHABLE` and `OBS_DEGRADED_INCOMPLETE` belong strictly to **Layer 3 (Observability State)**. Every physical package journey has an unambiguous deterministic ground truth (Layer 1). Observational ambiguity is an inferential limitation created by incomplete sensor masks or photographic degradation.

---

## 3. Unit of Analysis, Sampling, & Scenario Allocation

### 3.1 Unit of Analysis
The **independent unit of analysis** is the **individual package journey** ($N=60$). A single package journey consists of a physical package staged and tracked through four sequential checkpoints:
- **Checkpoint 1 ($CP_1$):** Hub / Seller Dispatch
- **Checkpoint 2 ($CP_2$):** Forward Doorstep Open Box Delivery (OBD)
- **Checkpoint 3 ($CP_3$):** Reverse Return Pickup Handover
- **Checkpoint 4 ($CP_4$):** Reverse Fulfillment Warehouse Receiving

Individual checkpoint scans ($4 \times 60 = 240$ observations) and reviewer ratings represent repeated, clustered observations nested within the 60 independent package journeys.

### 3.2 Full Scenario Allocation Matrix ($N=60$)

The 60 physical package journeys are partitioned across 8 realistic logistics scenario types:

| Scenario ID | Ground-Truth Physical State ($\mathcal{G}$, Layer 1) | Journey Range | Cell Size ($n$) | Injected Physical Staging Event | Target Observability State ($\Omega$, Layer 3) | Target Action ($\mathcal{D}$, Layer 5) |
|:---:|---|:---:|:---:|---|:---:|:---:|
| **SC-01** | `GT_INTACT` (Standard Intact) | $J_{01} - J_{15}$ | 15 | Package, seal, serial, and weight remain identical across all checkpoints. | `OBS_DETERMINABLE` | `DEC_APPROVE_REFUND` |
| **SC-02** | `GT_INTACT` (Permitted Bag Change) | $J_{16} - J_{23}$ | 8 | Outer flyer bag replaced at forward transit hub; primary brand box intact. | `OBS_DETERMINABLE` | `DEC_APPROVE_REFUND` |
| **SC-03** | `GT_FORWARD_TRANSIT_DAMAGE` | $J_{24} - J_{31}$ | 8 | Package crushed during forward transit; primary brand box creased, seal unbroken. | `OBS_DETERMINABLE` | `DEC_CHARGEBACK_CARRIER` |
| **SC-04** | `GT_DOORSTEP_SUBSTITUTION` | $J_{32} - J_{39}$ | 8 | Cheaper model substituted at forward delivery (replicates *Adilabad* case). | `OBS_DETERMINABLE` | `DEC_REJECT_REFUND` |
| **SC-05** | `GT_CUSTOMER_TAMPER` | $J_{40} - J_{47}$ | 8 | Customer swaps high-value phone with dummy unit before return pickup. | `OBS_DETERMINABLE` | `DEC_REJECT_REFUND` |
| **SC-06** | `GT_REVERSE_TRANSIT_TAMPER` | $J_{48} - J_{52}$ | 5 | Return flyer slit and retaped during reverse transit; internal item removed. | `OBS_DETERMINABLE` | `DEC_CHARGEBACK_CARRIER` |
| **SC-07** | `GT_CUSTOMER_TAMPER` / Degraded | $J_{53} - J_{56}$ | 4 | Pickup agent fails to record clear photo/weight scan at customer doorstep (glare/dark). | `OBS_DEGRADED_INCOMPLETE` | `DEC_HOLD_INVESTIGATION` |
| **SC-08** | `GT_CUSTOMER_TAMPER` / Ambiguous | $J_{57} - J_{60}$ | 4 | Scratch on smartphone screen; photos at $CP_2$ and $CP_3$ have glare over defect area. | `OBS_INDISTINGUISHABLE` | `DEC_HOLD_INVESTIGATION` |
| **TOTAL** | — | — | **60** | — | — | — |

---

## 4. Experimental Review Conditions: Isolating Evidence Linkage

### 4.1 Eliminating the Authenticity Confound and Narrowing the Intervention
In previous iterations, Condition D was described as featuring a "cryptographic chain-of-custody verification seal" that Condition C lacked, thereby confounding cross-stage linkage with perceived data authenticity. Furthermore, Condition D provides automated visual alignment and tare weight reconciliation curves that Condition C does not automate.

To establish methodological rigor:
1. **Equal Authenticity Cues:** Both Condition C and Condition D receive **identical cryptographic authenticity metadata**. In both conditions, each individual checkpoint record displays an identical tamper-evident verification stamp (*"SHA-256 Authenticated Checkpoint Record — Timestamp & Signature Verified"*).
2. **Equal Underlying Information:** Both conditions provide the exact same high-resolution photos, 0.1g digital scale readings, courier scan notes, and ISO-8601 timestamps across all four checkpoints ($CP_1, CP_2, CP_3, CP_4$).
3. **Narrowed Experimental Intervention (Combined Linked-Presentation & Automated Reconciliation):** Because Condition D provides both chronological record linkage AND automated visual delta alignment and tare weight curves, the treatment tested against Condition C is explicitly defined as a **combined linked-evidence presentation and automated-reconciliation intervention**:
   - In **Condition C (Information-Matched Control)**: Checkpoint records are presented as four disconnected, unaligned attachments/tabs. Reviewers must manually switch between tabs, manually visually compare unaligned photos, and mentally calculate weight differences across checkpoints.
   - In **Condition D (Combined Intervention Pipeline)**: Checkpoint records are presented in a unified chronological interface featuring automated side-by-side visual delta comparison ($CP_2$ forward delivery photos directly adjacent to $CP_3$ return pickup photos with synchronized pan/zoom), automated tare weight trajectory curves ($\Delta w = w_t - w_{\text{tare}}$), and automated weight delta variance anomaly flags.

### 4.2 Comprehensive Condition Specification Table

| Evaluation Parameter | Condition A (Baseline 0: Isolated Warehouse) | Condition B (Baseline 1: Disconnected Two-Point) | Condition C (Baseline 2: Disconnected Multi-Point Control) | Condition D (Proposed System: Combined Intervention Pipeline) |
|---|---|---|---|---|
| **Checkpoints Provided** | $CP_4$ only | $CP_1, CP_4$ | $CP_1, CP_2, CP_3, CP_4$ | $CP_1, CP_2, CP_3, CP_4$ |
| **Image Resolution & Quality** | Standardized 1080p | Standardized 1080p | Standardized 1080p | Standardized 1080p |
| **Tare Weight Precision** | Digital scale (0.1g) | Digital scale (0.1g) | Digital scale (0.1g) | Digital scale (0.1g) |
| **Authenticity Verification Badge** | Single-record stamp | Endpoint record stamps | **Identical SHA-256 stamps on all 4 records** | **Identical SHA-256 stamps on all 4 records** |
| **Visual Presentation Mode** | Single photo viewer | Two separate tabs | Four disconnected tabs | **Unified chronological timeline with side-by-side aligned delta viewer** |
| **Weight Trajectory Reconciliation** | Single point weight | Mental subtraction | Mental subtraction across 4 points | **Automated tare weight curve with variance delta flags** |
| **Reviewer Evaluation Form** | Standardized dropdown | Standardized dropdown | Standardized dropdown | Standardized dropdown (100% identical UI form) |
| **Adjudication Time Budget** | 3.0 minutes max | 3.0 minutes max | 3.0 minutes max | 3.0 minutes max |
| **Scientific Role** | Current industry warehouse baseline | Standard e-commerce support review baseline | **Information-matched control for Condition D** | **Tests combined intervention of linked presentation and automated reconciliation** |

---

## 5. Reviewer Allocation, Blinding, & Latin Square Balancing

### 5.1 Reviewer Allocation Table ($4 \times 4$ Balanced Latin Square)
To evaluate the 60 package journeys across all 4 conditions while preventing carry-over contamination and reviewer fatigue, a **$4 \times 4$ Latin Square balanced crossover design** is implemented across four independent reviewer cohorts ($R_1, R_2, R_3, R_4$) evaluating four 15-case blocks separated by a **48-hour washout period**:

| Evaluation Block | Case Range | Reviewer 1 ($R_1$) Condition | Reviewer 2 ($R_2$) Condition | Reviewer 3 ($R_3$) Condition | Reviewer 4 ($R_4$) Condition |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **Block 1 (Session 1)** | Journeys $J_{01} - J_{15}$ | **Condition A** (Isolated WH) | **Condition B** (Disconn. 2-Pt) | **Condition C** (Disconn. Multi) | **Condition D** (Linked Chain) |
| *Washout Period* | — | *48 hours* | *48 hours* | *48 hours* | *48 hours* |
| **Block 2 (Session 2)** | Journeys $J_{16} - J_{30}$ | **Condition B** (Disconn. 2-Pt) | **Condition C** (Disconn. Multi) | **Condition D** (Linked Chain) | **Condition A** (Isolated WH) |
| *Washout Period* | — | *48 hours* | *48 hours* | *48 hours* | *48 hours* |
| **Block 3 (Session 3)** | Journeys $J_{31} - J_{45}$ | **Condition C** (Disconn. Multi) | **Condition D** (Linked Chain) | **Condition A** (Isolated WH) | **Condition B** (Disconn. 2-Pt) |
| *Washout Period* | — | *48 hours* | *48 hours* | *48 hours* | *48 hours* |
| **Block 4 (Session 4)** | Journeys $J_{46} - J_{60}$ | **Condition D** (Linked Chain) | **Condition A** (Isolated WH) | **Condition B** (Disconn. 2-Pt) | **Condition C** (Disconn. Multi) |

### 5.2 Prevention of Carry-Over and Order Contamination
1. **Zero Case Re-Exposure:** Each reviewer evaluates any given physical package journey **exactly once**. A reviewer never evaluates the same physical package under multiple conditions.
2. **Within-Block Randomization:** Within each 15-case block, case presentation order is independently randomized for each reviewer.
3. **Condition Masking:** Reviewers are not informed of condition names ("Condition A", "Condition D"); the UI presents each case neutrally as "Case Evaluation Session".
4. **Case Anonymization & Ground-Truth Blinding:** Sequential Journey IDs ($J_{01}-J_{60}$) are internal physical staging indices and are strictly withheld from reviewers. In all evaluation sessions, cases are presented under randomized, blinded Tracking Codes (`CASE-XXXX`) generated via a confidential random permutation table held exclusively by the trial coordinator. The plaintext truth ledger is embargoed until all 240 evaluations are completed, preventing reviewers from linking case codes to scenario groups.

---

## 6. Mathematical Definitions of Evaluated Outcomes

### 6.1 Objective Evaluation Mapping Across All 60 Journeys

Let each journey $i \in \{1, \dots, 60\}$ evaluated under condition $k \in \{A, B, C, D\}$ have:
- Physical ground truth $\mathcal{G}_i \in \{\text{GT\_INTACT}, \text{GT\_FORWARD\_TRANSIT\_DAMAGE}, \text{GT\_DOORSTEP\_SUBSTITUTION}, \text{GT\_CUSTOMER\_TAMPER}, \text{GT\_REVERSE\_TRANSIT\_TAMPER}\}$.
- Condition-specific target observability state $\Omega_{ik}^* \in \{\text{OBS\_DETERMINABLE}, \text{OBS\_INDISTINGUISHABLE}, \text{OBS\_DEGRADED\_INCOMPLETE}\}$. Observability $\Omega_{ik}^*$ is defined strictly by objective, evidence-based criteria governing what an ideal observer can deduce from the sensory data mask $M_k$:
  - Under Condition A ($CP_4$ only) and Condition B ($CP_1, CP_4$), transitions occurring across unobserved intermediate checkpoints lack necessary baseline evidence, rendering discrepancy stages objectively indistinguishable ($\Omega_{iA}^* = \Omega_{iB}^* = \text{OBS\_INDISTINGUISHABLE}$ for SC-02 through SC-06).
  - Under Conditions C and D, all four checkpoints ($CP_1, CP_2, CP_3, CP_4$) are provided with identical 1080p photos, 0.1g digital scale readings, and SHA-256 stamps ($M_C = M_D$). Therefore, objective observability is **identically distributed across Conditions C and D**:
    $$\Omega_{iC}^* = \Omega_{iD}^*, \quad \forall i \in \{1, \dots, 60\}$$
    We do NOT assume Condition C is ambiguous merely because its interface requires manual tab navigation. Both Condition C and Condition D are objectively determinable ($\Omega^* = \text{OBS\_DETERMINABLE}$) for all clear journeys ($J_{01}-J_{52}$), degraded ($\Omega^* = \text{OBS\_DEGRADED\_INCOMPLETE}$) for dark/blurry captures ($J_{53}-J_{56}$), and indistinguishable ($\Omega^* = \text{OBS\_INDISTINGUISHABLE}$) for glare-obscured captures ($J_{57}-J_{60}$). The experimental contrast between Condition D and Condition C evaluates the extent to which automated alignment and tare curves help human adjudicators realize this latent determinability against human cognitive friction.
- Reviewer attribution $\mathcal{A}_{ijk} \in \{\text{ATTR\_STAGE\_*}, \text{ATTR\_CONFIRMED\_LEGITIMATE}, \text{ATTR\_ABSTAIN\_*}\}$ rendered by reviewer $j$ under condition $k$.
- Operational platform decision $\mathcal{D}_{ijk} \in \{\text{DEC\_*}\}$.

$$\text{Adjudication Outcome}(i, j, k) = \begin{cases}
\textbf{Correct Attribution}, & \text{if } \Omega_{ik}^* = \text{OBS\_DETERMINABLE} \text{ and } \text{Match}(\mathcal{A}_{ijk}, \mathcal{G}_i) \\
\textbf{Correct Abstention}, & \text{if } \Omega_{ik}^* \neq \text{OBS\_DETERMINABLE} \text{ and } \mathcal{A}_{ijk} \in \{\text{ATTR\_ABSTAIN\_INDISTINGUISHABLE}, \text{ATTR\_ABSTAIN\_DEGRADED}\} \\
\textbf{Unsupported Blame}, & \text{if } \Omega_{ik}^* \neq \text{OBS\_DETERMINABLE} \text{ and } \mathcal{A}_{ijk} \in \{\text{ATTR\_STAGE\_*}\} \\
\textbf{Unnecessary Abstention}, & \text{if } \Omega_{ik}^* = \text{OBS\_DETERMINABLE} \text{ and } \mathcal{A}_{ijk} \in \{\text{ATTR\_ABSTAIN\_*}\} \\
\textbf{Misattribution}, & \text{if } \Omega_{ik}^* = \text{OBS\_DETERMINABLE} \text{ and } \neg\text{Match}(\mathcal{A}_{ijk}, \mathcal{G}_i) \text{ and } \mathcal{A}_{ijk} \in \{\text{ATTR\_STAGE\_*}\}
\end{cases}$$

Where $\text{Match}(\mathcal{A}, \mathcal{G})$ is defined as:
- $\text{Match}(\text{ATTR\_STAGE\_FORWARD\_TRANSIT}, \text{GT\_FORWARD\_TRANSIT\_DAMAGE}) = \text{True}$
- $\text{Match}(\text{ATTR\_STAGE\_DOORSTEP\_DELIVERY}, \text{GT\_DOORSTEP\_SUBSTITUTION}) = \text{True}$
- $\text{Match}(\text{ATTR\_STAGE\_CONSUMER\_CUSTODY}, \text{GT\_CUSTOMER\_TAMPER}) = \text{True}$
- $\text{Match}(\text{ATTR\_STAGE\_REVERSE\_TRANSIT}, \text{GT\_REVERSE\_TRANSIT\_TAMPER}) = \text{True}$
- $\text{Match}(\text{ATTR\_CONFIRMED\_LEGITIMATE}, \text{GT\_INTACT}) = \text{True}$

### 6.2 Primary Outcome Metrics (Evaluated Across Common Set of All 60 Journeys)

#### 1. Overall Adjudication Accuracy ($OAA$)
To fairly compare decisions across the exact same 60 journeys while accounting for condition-specific observability differences, $OAA$ evaluates whether the reviewer's decision matches the condition-specific normative standard $\Omega_{ik}^*$:

$$Y_{ijk} = \begin{cases}
1, & \text{if } (\Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \text{Match}(\mathcal{A}_{ijk}, \mathcal{G}_i)) \lor (\Omega_{ik}^* \neq \text{OBS\_DETERMINABLE} \land \mathcal{A}_{ijk} \in \{\text{ATTR\_ABSTAIN\_*}\}) \\
0, & \text{otherwise}
\end{cases}$$

$$OAA_k = \frac{1}{60} \sum_{i=1}^{60} Y_{ijk}$$

> [!IMPORTANT]
> **Objective Evidence-Based Observability Standard:** $OAA$ evaluates whether a reviewer's decision matches the objective information theoretically deducible from the condition's data mask $M_k$. Under Condition A ($CP_4$ only) and Condition B ($CP_1, CP_4$), intermediate discrepancies are objectively unobservable due to missing handovers ($\Omega_{iA}^* = \Omega_{iB}^* = \text{OBS\_INDISTINGUISHABLE}$), meaning appropriate abstention is the optimal decision ($Y = 1$ if abstained). Under Conditions C and D, all four checkpoints are present ($M_C = M_D$), meaning both conditions share the identical objective standard ($\Omega_{iC}^* = \Omega_{iD}^*$). For determinable journeys ($J_{01}-J_{52}$), optimal performance requires correct stage attribution; for corrupted journeys ($J_{53}-J_{60}$), optimal performance requires appropriate abstention. Scoring on the identical 60 journeys tests whether automated alignment in Condition D reduces human cognitive errors and mental calculation failures relative to the unaligned Condition C.

#### 2. Operational Decision Alignment ($ODA$)
Measures whether the platform's business decision $\mathcal{D}_{ijk}$ matches the condition-specific normative policy $\mathcal{D}_{ik}^* = \mathcal{D}^*(\mathcal{G}_i, \Omega_{ik}^*)$ across all 60 journeys:

$$ODA_k = \frac{1}{60} \sum_{i=1}^{60} \mathbb{I}(\mathcal{D}_{ijk} = \mathcal{D}_{ik}^*)$$

Where the condition-specific target operational decision $\mathcal{D}_{ik}^*$ is defined as:
$$\mathcal{D}_{ik}^* = \mathcal{D}^*(\mathcal{G}_i, \Omega_{ik}^*) = \begin{cases}
\text{DEC\_HOLD\_INVESTIGATION}, & \text{if } \Omega_{ik}^* \in \{\text{OBS\_INDISTINGUISHABLE}, \text{OBS\_DEGRADED\_INCOMPLETE}\} \\
\text{DEC\_APPROVE\_REFUND}, & \text{if } \Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \mathcal{G}_i = \text{GT\_INTACT} \\
\text{DEC\_CHARGEBACK\_CARRIER}, & \text{if } \Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \mathcal{G}_i \in \{\text{GT\_FWD\_TRANSIT\_DAMAGE}, \text{GT\_REV\_TRANSIT\_TAMPER}\} \\
\text{DEC\_REJECT\_REFUND}, & \text{if } \Omega_{ik}^* = \text{OBS\_DETERMINABLE} \land \mathcal{G}_i \in \{\text{GT\_DOORSTEP\_SUBSTITUTION}, \text{GT\_CUSTOMER\_TAMPER}\}
\end{cases}$$

### 6.3 Secondary Outcome Metrics

#### 1. Discrepancy Macro F1 (Secondary Metric with Coherent Evaluation Set)
Evaluated across the **four physical handover discrepancy classes** ($c \in \{1, 2, 3, 4\}$) over the **common universe of all 60 journeys**:

$$\begin{aligned}
TP_c &= \sum_{i=1}^{60} \mathbb{I}(\mathcal{G}_i = g_c \land \mathcal{A}_{ijk} = a_c) \\
FP_c &= \sum_{i=1}^{60} \mathbb{I}(\mathcal{G}_i \neq g_c \land \mathcal{A}_{ijk} = a_c) \\
FN_c &= \sum_{i=1}^{60} \mathbb{I}(\mathcal{G}_i = g_c \land \mathcal{A}_{ijk} \neq a_c) \\
\text{Precision}_c &= \frac{TP_c}{TP_c + FP_c}, \quad \text{Recall}_c = \frac{TP_c}{TP_c + FN_c}, \quad F1_c = \frac{2 \cdot \text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c} \\
\text{Discrepancy Macro F1} &= \frac{1}{4} \sum_{c=1}^{4} F1_c
\end{aligned}$$

> [!NOTE]
> **Evaluation Set Coherence:** By summing $TP_c$, $FP_c$, and $FN_c$ over the identical set of 60 journeys, this formula eliminates previous denominator asymmetry. If a reviewer inappropriately blames class $c$ on an intact journey or ambiguous journey, it is properly captured as $FP_c$. If a reviewer abstains or misidentifies class $c$, it is properly captured as $FN_c$.

#### 2. Appropriate Abstention Rate ($AAR$)
Evaluated strictly on the condition-specific ambiguous or degraded journeys for condition $k$:

$$\mathcal{N}_{\text{ambig}, k} = \{i : \Omega_{ik}^* \neq \text{OBS\_DETERMINABLE}\}, \quad |\mathcal{N}_{\text{ambig}, k}| = \sum_{i=1}^{60} \mathbb{I}(\Omega_{ik}^* \neq \text{OBS\_DETERMINABLE})$$

$$AAR_k = \frac{1}{|\mathcal{N}_{\text{ambig}, k}|} \sum_{i \in \mathcal{N}_{\text{ambig}, k}} \mathbb{I}(\mathcal{A}_{ijk} \in \{\text{ATTR\_ABSTAIN\_INDISTINGUISHABLE}, \text{ATTR\_ABSTAIN\_DEGRADED}\})$$

#### 3. Unsupported Blame Rate ($UBR$)
Evaluated strictly on the condition-specific ambiguous or degraded journeys for condition $k$:

$$UBR_k = \frac{1}{|\mathcal{N}_{\text{ambig}, k}|} \sum_{i \in \mathcal{N}_{\text{ambig}, k}} \mathbb{I}(\mathcal{A}_{ijk} \in \{\text{ATTR\_STAGE\_FORWARD\_TRANSIT}, \text{ATTR\_STAGE\_DOORSTEP\_DELIVERY}, \text{ATTR\_STAGE\_CONSUMER\_CUSTODY}, \text{ATTR\_STAGE\_REVERSE\_TRANSIT}\})$$

*(Note: $AAR_k + UBR_k \le 1$; a reviewer may also erroneously confirm legitimacy).*

#### 4. Unnecessary Abstention Rate ($UAR$)
Evaluated strictly on the condition-specific determinable journeys for condition $k$:

$$\mathcal{N}_{\text{det}, k} = \{i : \Omega_{ik}^* = \text{OBS\_DETERMINABLE}\}, \quad |\mathcal{N}_{\text{det}, k}| = \sum_{i=1}^{60} \mathbb{I}(\Omega_{ik}^* = \text{OBS\_DETERMINABLE})$$

$$UAR_k = \frac{1}{|\mathcal{N}_{\text{det}, k}|} \sum_{i \in \mathcal{N}_{\text{det}, k}} \mathbb{I}(\mathcal{A}_{ijk} \in \{\text{ATTR\_ABSTAIN\_INDISTINGUISHABLE}, \text{ATTR\_ABSTAIN\_DEGRADED}\})$$

#### 5. Reviewer Time-to-Decision
Mean adjudication duration per case (seconds) recorded via automated client-side timestamps from case presentation to form submission.

---

## 7. Statistical Analysis Plan: Paired & Clustered Inference

### 7.1 Primary Comparison: Testing Combined Linked-Intervention (Condition D vs. Condition C)
Condition D and Condition C provide **identical underlying sensory information and identical SHA-256 cryptographic authenticity stamps**. Thus, comparing Condition D against Condition C evaluates the specific impact of the **combined linked-evidence presentation and automated visual/weight reconciliation pipeline**:
1. **Primary Adjudication Success ($OAA$) Comparison (Clustered Bootstrap & Paired Permutation):**
   The primary hypothesis $H_{1}: OAA_{\text{Cond D}} > OAA_{\text{Cond C}}$ across the 60 journeys is evaluated using **clustered bootstrap resampling ($B=2,000$ iterations) clustered at the package journey level ($J_i$)**:
   - In each bootstrap sample $b \in \{1, \dots, 2000\}$, 60 journeys are drawn with replacement, preserving within-journey correlation across conditions.
   - We compute $\Delta OAA^{(b)} = OAA_{\text{Cond D}}^{(b)} - OAA_{\text{Cond C}}^{(b)}$.
   - We report point estimates, bootstrap standard error, and 95% percentile confidence interval $[\Delta OAA_{2.5\%}, \Delta OAA_{97.5\%}]$.
   - A non-parametric paired permutation test (5,000 permutations shuffling C vs D within journey) provides the two-sided empirical permutation $p$-value.
2. **Binary Decision Concordance (McNemar's Paired Test):**
   McNemar's test is applied strictly to paired binary adjudication success $Y_i \in \{0, 1\}$ across the matched 60 package journeys:
   - Contingency discordance pairs ($b$: correct in D, incorrect in C; $c$: correct in C, incorrect in D) evaluated via exact binomial paired test.
3. **Secondary Multiclass Discrepancy Macro F1 Comparison:**
   Evaluated using the same journey-clustered bootstrap ($B=2,000$) on the secondary 4-class Discrepancy Macro F1 metric.

### 7.2 Secondary Comparison: Information Quantity (Condition C vs. B vs. A)
To evaluate the incremental value of collecting more checkpoint photos (holding linkage constant), Condition C is contrasted against Condition B and Condition A via paired bootstrap comparisons of $OAA$ and Macro F1.

### 7.3 Inter-Rater Reliability & Statistical Modeling: Reviewer Fixed Effects

#### 1. Methodological Justification for Reviewer Fixed Effects over Random Effects
In the previous protocol iteration, a Generalized Linear Mixed-Effects Model (GLMM) with a reviewer random intercept $v_j \sim \mathcal{N}(0, \sigma_{\text{reviewer}}^2)$ was proposed. However, with only **four human reviewers ($R=4$)**, estimating a random-effects variance component $\sigma_{\text{reviewer}}^2$ is statistically problematic:
- Estimating variance components requires a sufficiently large sample of cluster levels (standard statistical guidelines recommend at least 10–20 clusters; $R=4$ is severely underpowered for distribution estimation).
- Maximum likelihood algorithms frequently encounter singular fits (boundary estimates $\hat{\sigma}^2 = 0$) or unstable, uninterpretable random-effect estimates.
- **Adopted Solution (Reviewer Fixed Effects):** We model reviewers as **fixed categorical covariates** (dummy indicators $R_2, R_3, R_4$, taking $R_1$ as the reference baseline). This directly and reliably adjusts for individual reviewer differences in adjudication skill, stringency, and calibration without imposing distributional assumptions on a sample of 4 raters.

#### 2. Statistical Model Specification
To model adjudication success $Y_{ij} \in \{0, 1\}$ for package journey $i \in \{1, \dots, 60\}$ evaluated by reviewer $j \in \{1, \dots, 4\}$:

$$\text{logit}(P(Y_{ij} = 1)) = \beta_0 + \beta_B \cdot \text{Cond}_B + \beta_C \cdot \text{Cond}_C + \beta_D \cdot \text{Cond}_D + \sum_{r=2}^{4} \gamma_r \cdot \text{Reviewer}_{jr}$$

- Reference condition: Condition A (Isolated Warehouse).
- Treatment effect of primary interest: $\Delta \beta = \beta_D - \beta_C$.
- Standard errors are computed using **cluster-robust standard errors clustered at the package journey level ($J_i$)** to account for repeated measurements across the Latin Square crossover design.

#### 3. Pre-Experimental Reviewer Calibration Trial (Gate E-3: Rubric & Agreement Calibration)
Gate E-3 is strictly defined as a **text-based rubric and inter-reviewer agreement calibration**. Prior to launching the crossover trial, all 4 reviewers ($R_1, R_2, R_3, R_4$) independently evaluate the **SAME 10 benchmark case scenarios** (`C01`-`C10`) based on standardized text and evidence descriptions. Multi-rater Fleiss' Kappa ($\kappa$) and Krippendorff's Alpha ($\alpha$) are calculated to verify consistent taxonomic interpretation and appropriate abstention. The mandatory passing threshold is $\kappa \ge 0.60$. This calibration establishes rubric comprehension; it does **not** validate visual-interface proficiency.

#### 4. Separate Unscored Interface Familiarization Step (Pre-Trial Tool Orientation)
Following successful clearance of Gate E-3 and immediately prior to Session 1, reviewers complete a **separate, unscored interface familiarization step**:
- Reviewers are oriented to the interactive controls across all four experimental interfaces (single photo viewer in Cond A, two tabs in Cond B, four tabs in Cond C, and the chronological timeline with side-by-side synchronized pan/zoom and tare curves in Cond D).
- Practice is conducted using **2–3 dummy orientation cases** (`ORIENT-01`, `ORIENT-02`, `ORIENT-03`).
- **Strict Experimental Stimuli Prohibition:** The 60 experimental package journeys ($J_{01}-J_{60}$) are **STRICTLY PROHIBITED** from use in interface familiarization to prevent preview or pre-exposure.
- **Unscored:** No accuracy or latency metrics are recorded.

---

## 8. Pilot Scope Boundary & Economic Sensitivity Specifications

> [!WARNING]
> **Exploratory Feasibility Pilot Boundary:**  
> With $N=60$ package journeys, this study is formally designated as an **Exploratory Feasibility Pilot**.  
>  
> **What this pilot CAN establish:**  
> 1. Technical feasibility of linking multi-checkpoint visual and weight evidence;  
> 2. Proof-of-concept demonstration that cross-stage evidence linkage improves human attribution accuracy compared to unlinked raw evidence;  
> 3. Measurement of human tendency to assign unsupported blame under degraded or ambiguous observations.  
>  
> **What this pilot CANNOT establish:**  
> 1. National prevalence rates of return fraud, courier theft, or product substitution;  
> 2. Real-world courier compliance under commercial delivery pressure;  
> 3. Platform-wide financial savings.

All economic figures (wages, dispute costs) are strictly **Uncalibrated Sensitivity Parameters** evaluated across parametric ranges (₹500 to ₹50,000 per dispute) in simulation grids.

---

## 9. Pre-Execution Gate Requirements (Pilot Execution Gated)

Execution of physical package staging and reviewer adjudication is strictly gated until the following three Pre-Experimental Gates are cleared:

| Pre-Experimental Gate ID | Requirement | Verification Artifact Required | Status |
|:---:|---|---|:---:|
| **Gate E-1** | Protocol Freeze & Preregistration | Timestamped Git commit hash of Protocol v2.5.0 on public repository | **PENDING (Awaiting Lead Approval)** |
| **Gate E-2** | Truth Ledger Hash Pre-Commitment | SHA-256 hash manifest committed to Git before physical staging (plaintext truth ledger strictly embargoed) | **PENDING (Awaiting Lead Approval)** |
| **Gate E-3** | Reviewer Calibration Trial | 10-case text-based rubric calibration completed with four real independent Reviewers $R_1-R_4$; baseline agreement $\kappa \ge 0.60$ documented; separate unscored UI familiarization | **PENDING (Awaiting 4 Real Reviewers)** |

> [!NOTE]
> **Prior-Art Literature Clearance (Gate M-5):** Full-text acquisition and review of Elia et al. (2024, Emerald Insight) is formally designated as **Pre-Publication Gate M-5**. It does NOT block physical packaging or reviewer adjudication; research-gap claims remain strictly bounded to exploratory feasibility.

Physical package staging, image capture, and human reviewer sessions will **NOT** commence until Pre-Experimental Gates E-1, E-2, and E-3 are completed.

