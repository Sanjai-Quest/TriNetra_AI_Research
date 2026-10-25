# Revised Phase 1 Experimental Research Protocol (Reviewed v1)

> **Protocol Version:** 1.1.0 (Reviewed)  
> **Date:** 2026-10-24  
> **Reviewer:** Independent Research-Methodology Reviewer  
> **Supersedes:** `research/phase1_experiment_protocol.md` (original preserved)  
> **Corrections Applied:** Separated physical ground truth / evidence visibility / observability class / operational decision; labeled trial as exploratory feasibility study; marked cost parameters as sensitivity assumptions; aligned Study A schema with `physical_observations_schema.md`; added reviewer recruitment specification; added statistical considerations.  
> **Core Rule:** Strictly non-synthetic, unrigged evaluation. No nationwide error rate claims. No monetary savings claims from mock trial.

---

## 1. Study Title & Core Research Questions

### 1.1 Working Title
*Evidence Continuity Across Open Box Delivery and Reverse Logistics: An Exploratory Feasibility Study of E-Commerce Product Disputes in India*

### 1.2 Primary Research Question
> **Primary RQ:**  
> *"How does evidence captured at Open Box Delivery and subsequent return/warehouse handovers affect the ability to distinguish product or fulfilment errors, logistics handling changes and unresolved disputes in Indian e-commerce?"*

### 1.3 Sub-Questions (RQs)
- **RQ1 (Documentary Failure Taxonomy):** What failure modes are documented in Indian official grievance data, marketplace OBD policies, and consumer commission decisions, and at which transaction handover do evidence gaps occur?
- **RQ2 (Minimal Evidentiary Fields):** Which physical telemetry fields (SKU/variant identifier, seal status, tare mass, repeated mass readings, timestamped images, handover acknowledgement) are necessary and sufficient to distinguish competing explanations for parcel discrepancies?
- **RQ3 (Reviewer Accuracy & Agreement):** Does a structured evidence packet with explicit abstention (`INDISTINGUISHABLE`) improve independent reviewers' agreement (Fleiss' κ) and accuracy against known ground truth compared with an unstructured complaint narrative or a basic checklist?
- **RQ4 (Operational Feasibility):** What is the estimated inspection time cost of multi-point handover telemetry under sensitivity-tested operational assumptions?

### 1.4 Study Scope Declaration

> [!IMPORTANT]
> This protocol describes an **exploratory feasibility study** using a controlled mock physical trial. It does **not** generate claims about:
> - Nationwide delivery-agent compliance rates
> - Real-world operational error frequencies
> - Monetary cost savings from deployment
> - Population-level fraud prevalence
>
> All cost, wage, and dispute-rate parameters in Study D are **sensitivity assumptions**, not empirical estimates.

---

## 2. Conceptual Separation: Four Layers

This protocol rigorously separates four distinct analytical layers. Every experimental scenario and every baseline evaluation must specify all four independently.

### 2.1 Layer Definitions

| Layer | Definition | Values | Determined By |
|---|---|---|---|
| **Physical Ground Truth** | What actually happened to the item across its custody journey | `LEGITIMATE`, `FULFILMENT_ERROR`, `TRANSIT_DAMAGE`, `POST_DELIVERY_CHANGE`, `INDISTINGUISHABLE` | Lead experimenter (ex-ante, blinded from evaluators) |
| **Evidence Visibility** | What physical evidence a reviewer or model is permitted to observe for a given evaluation | Mask 0 through Mask 3 (see §5.3) | Experimental design (controlled per evaluation condition) |
| **Observability Class** | Whether the ground truth is detectable, ambiguous, or unobservable under the given evidence visibility | `DETECTABLE` (ground truth inferable from available evidence), `AMBIGUOUS` (evidence suggests multiple competing explanations), `UNOBSERVABLE` (available evidence is insufficient to distinguish ground truth) | Derived from the interaction of ground truth × evidence visibility |
| **Operational Decision** | The action recommended by a reviewer or decision model | `PASS` (accept return/delivery), `REVIEW` (escalate for additional inspection), `HOLD` (reject or quarantine pending further evidence) | Output of the reviewer or model under evaluation |

### 2.2 How These Layers Interact

```
Physical Ground Truth        Evidence Visibility          Observability Class     Operational Decision
(what happened)              (what is observed)           (can truth be inferred?) (what action is taken)
────────────────────    ×    ─────────────────────   →    ────────────────────  →  ────────────────────
FULFILMENT_ERROR             Mask 0 (claim text only)     UNOBSERVABLE            (Depends on model/reviewer)
FULFILMENT_ERROR             Mask 3 (full custody)        DETECTABLE              (Depends on model/reviewer)
POST_DELIVERY_CHANGE         Mask 1 (warehouse only)      AMBIGUOUS               (Depends on model/reviewer)
INDISTINGUISHABLE            Mask 3 (full custody)        UNOBSERVABLE            (Correct answer: REVIEW)
```

> [!IMPORTANT]
> A correct decision model should:
> - Output `PASS` when observability class is `DETECTABLE` and ground truth is `LEGITIMATE`
> - Output `HOLD` when observability class is `DETECTABLE` and ground truth is an error/change
> - Output `REVIEW` when observability class is `AMBIGUOUS` or `UNOBSERVABLE`
> 
> A model that outputs `PASS` or `HOLD` for `UNOBSERVABLE` cases exhibits false precision. This is an error, not a feature.

---

## 3. Experimental Architecture: Four Linked Studies

```
STUDY A: Documentary Evidence Map & Failure Mode Taxonomy
  • Sources: NCH grievance data, DCDRC orders, OBD terms
  • Output: Taxonomy of documented dispute scenarios
                             │
                             ▼
STUDY B: Controlled Mock Physical Trial (Exploratory, n=60)
  • 60 physical units across 3 categories
  • 5 custody checkpoints per unit
  • 8 controlled scenario injections
                             │
                             ▼
STUDY C: Blinded Multi-Reviewer Adjudication
  • 3 human reviewers + 4 baseline decision models
  • 4 evidence visibility masks per scenario
  • Metrics: accuracy, agreement, abstention rate, time
                             │
                             ▼
STUDY D: Operational Feasibility Sensitivity Model
  • All parameters are sensitivity assumptions
  • Output: Break-even curves under varied assumptions
```

---

## 4. Study A: India-Focused Documentary Evidence Map

### 4.1 Objective
Construct an empirical taxonomy of documented e-commerce delivery and return failures in India, mapping where the chain of custody breaks down.

### 4.2 Data Sources & Inclusion Requirements
1. **Official Grievance Statistics:** NCH annual grievance data (PIB, 10 Sep 2026).
2. **Statutory Framework:** Consumer Protection (E-Commerce) Rules, 2020 and 2026 amendments.
3. **Adjudicated Legal Cases:** DCDRC orders verified via primary text or accredited secondary legal reporters (LiveLaw, Casemine). Cases verified only via commercial news reports (e.g., Financial Express) must be marked as `SECONDARY_NEWS_REPORT_ONLY`.
4. **Marketplace Policies:** Published OBD Terms (Flipkart, 2026) and return policies.

### 4.3 Case Coding Schema (Aligned with `physical_observations_schema.md`)

Each documented case is coded into the following schema **without inferring fraudulent intent**:

| Field | Type | Values | Alignment with `physical_observations_schema.md` |
|---|---|---|---|
| `case_id` | String | Official docket or policy reference | — |
| `checkpoint_type` | String | `SUPPLIER_DISPATCH`, `WAREHOUSE_INBOUND`, `CARRIER_HUB`, `DELIVERY_HANDOFF`, `RETURN_RECEIVING` | Matches `checkpoint_type` in schema |
| `disputed_symptom` | String | `MISSING_COMPONENT`, `WRONG_VARIANT`, `PHYSICAL_DAMAGE`, `COUNTERFEIT_SUBSTITUTION`, `UNRECORDED_STATE_CHANGE` | — |
| `packaging_state` | String | `ORIGINAL_SEALED`, `REPACKAGED`, `OPENED`, `DAMAGED_CRUSHED`, `UNKNOWN` | Matches `packaging_state` in schema |
| `seal_status` | String | `INTACT`, `TAMPER_EVIDENT_VOID`, `BROKEN_MISSING`, `NOT_APPLICABLE` | Matches `seal_status` in schema |
| `evidence_available` | String | Free text: photos, videos, carrier scan logs, scale readings | Maps to `evidence_completeness` |
| `evidence_missing` | String | Free text: handover receipt, tare weight, serial number | Maps to `evidence_completeness` |
| `judicial_finding` | String | `DEFICIENCY_IN_SERVICE`, `UNFAIR_TRADE_PRACTICE`, `DISMISSED`, `NOT_APPLICABLE` | — |
| `verification_level` | String | `PRIMARY_ORDER_REVIEWED`, `ACCREDITED_LEGAL_REPORT`, `SECONDARY_NEWS_REPORT`, `POLICY_DOCUMENT` | New field — tracks evidentiary basis of the case itself |

---

## 5. Study B: Controlled Physical Experiment Protocol

### 5.1 Study Classification

> [!WARNING]
> This is an **exploratory feasibility study**. The sample size (n=60) has not been justified by a formal power analysis. Results will indicate feasibility and generate effect-size estimates for future confirmatory studies. They will not support population-level generalizations.

### 5.2 Physical Unit Cohort

The trial utilizes **60 physical units** spanning 3 high-dispute merchandise categories:

| Category | Unit Count | Target Items | Typical Mass Range | Primary Failure Vulnerabilities |
|---|:---:|---|:---:|---|
| **Consumer Electronics** | 20 | Smartphones, TWS Earbuds, Power Banks, Smartwatches | 150g – 800g | Model variant swaps, component stripping, accessory omission |
| **Footwear** | 20 | Branded Sneakers, Running Shoes, Formal Leather Shoes | 600g – 1400g | Size/variant confusion, sole wear, counterfeit substitution |
| **Apparel & Accessories** | 20 | Boxed Watches, Branded Shirts, Sunglasses | 100g – 500g | Tag switching, cosmetic scratching, missing protective pouches |

### 5.3 Standardized Measurement Instruments

Instruments aligned with `physical_observations_schema.md`:

| Instrument | Schema `instrument_type` | Precision | Protocol |
|---|---|---|---|
| Calibrated digital scale (BLE) | `BLE_SCALE` | ±0.1g (±0.5g for units > 1kg) | 3 repeated readings per checkpoint (`repeated_readings`) |
| Standardized smartphone camera | `VISION_CAMERA` | 12MP, 500-lux lighting | Standardized angles per item category |
| Handheld barcode scanner | `BARCODE_SCANNER` | Decode confidence ≥ 0.95 | Code-128 and 2D DataMatrix |

### 5.4 Checkpoint Traversal Pipeline

Every physical unit traverses 5 sequential custody checkpoints:

| Checkpoint | Schema `checkpoint_type` | Activities |
|:---:|---|---|
| CP₁ | `SUPPLIER_DISPATCH` | Initial gross mass, tare mass, serial/IMEI scan, tamper-evident seal photo |
| CP₂ | `CARRIER_HUB` | Gross parcel mass, barcode scan, outer carton condition |
| CP₃ | `DELIVERY_HANDOFF` | Outer seal opening, visual component check, model/color/accessory verification, OTP simulation |
| CP₄ | `RETURN_RECEIVING` (doorstep) | Doorstep return pickup: physical condition classification, pickup scale reading |
| CP₅ | `WAREHOUSE_INBOUND` | Intake weighing, seal integrity check, serial audit, visual surface grading |

### 5.5 Controlled Experimental Scenarios (n=60)

The 60 cases are partitioned into 8 scenario types with explicit ground truth and observability class mapping:

| Scenario | Count | Physical Ground Truth | Description | Expected Observability at Mask 3 |
|---|:---:|---|---|---|
| 1. Clean Legitimate Journey | 15 | `LEGITIMATE` | Authentic product, fully intact, zero changes | `DETECTABLE` |
| 2. Supplier Fulfilment Error | 8 | `FULFILMENT_ERROR` | Wrong color/variant packed at CP₁ | `DETECTABLE` (SKU mismatch visible) |
| 3. Doorstep OBD Catch | 7 | `FULFILMENT_ERROR` | Visible defect/missing item spotted at CP₃ | `DETECTABLE` |
| 4. Transit Damage | 6 | `TRANSIT_DAMAGE` | Crushed packaging, mass drop between CP₁ and CP₂ | `DETECTABLE` (mass delta > 2σ) |
| 5. Post-Delivery Substitution | 8 | `POST_DELIVERY_CHANGE` | Item swapped for counterfeit/dummy between CP₃ and CP₄ | `DETECTABLE` (if mass/serial changes exceed thresholds) |
| 6. Legitimate Repackaging | 6 | `LEGITIMATE` | Authorized carton change at CP₂ (tare delta) | `AMBIGUOUS` (tare change mimics tampering) |
| 7. Missing Custody Scans | 5 | Varies | CP₂ or CP₄ records omitted | `UNOBSERVABLE` (insufficient evidence) |
| 8. Observationally Indistinguishable | 5 | `INDISTINGUISHABLE` | Modification within sensor noise (Δm < 2σ) | `UNOBSERVABLE` |

#### Ground-Truth Status Specification

Ground truth is established **ex-ante** by the lead experimenter and held strictly private from evaluators:

- `LEGITIMATE`: Unit conforms to purchase order throughout journey.
- `FULFILMENT_ERROR`: Incorrect product, variant, or accessory packed prior to dispatch.
- `TRANSIT_DAMAGE`: Damage or loss occurring between dispatch and delivery.
- `POST_DELIVERY_CHANGE`: Substitution, wear, or component removal between delivery and return pickup.
- `INDISTINGUISHABLE`: Physical discrepancy Δm ≤ 2σ_instrument or legitimate repackaging indistinguishable from tampering without internal teardown.

### 5.6 Statistical Considerations

**Minimum detectable effect:** With n=60 units, 3 reviewers, and 4 visibility masks, the study generates 720 reviewer-case-mask observations (60 × 3 × 4). However, the per-cell sample sizes (e.g., n=5 for Scenario 7 and 8) are small.

**Appropriate analyses:**
- Fleiss' κ for inter-rater agreement (3 reviewers × 4 masks = 12 κ estimates)
- Descriptive accuracy rates against known ground truth
- Confidence intervals rather than p-values for exploratory estimates

**Inappropriate analyses (must not be performed):**
- Hypothesis tests claiming statistically significant differences between baselines at α=0.05 without a priori power analysis
- Population-level prevalence estimates from 60 controlled units
- Causal claims about delivery-agent behavior from a mock trial

---

## 6. Study C: Multi-Reviewer Adjudication Benchmark

### 6.1 Reviewer Cohort & Blinding

- **Human Evaluators:** 3 independent reviewers, recruited from pools with e-commerce operations or consumer dispute experience. Training protocol must be documented (training materials, duration, calibration exercises).
- **Blinding:** Reviewers are blinded to (a) ground truth, (b) other reviewers' scores, and (c) which scenarios are injected controls vs. legitimate journeys.

### 6.2 Competing Baselines Evaluated

Each baseline receives **the same evidence** for each comparison (matched evidence visibility mask):

| Baseline | Input | Decision Logic |
|---|---|---|
| **B1: Unstructured Narrative** | Raw consumer dispute text and stated return reason only (Mask 0) | Reviewer's judgment from complaint text |
| **B2: Single-Signal Probes** | One signal per sub-probe: (2A) SKU match, (2B) gross mass delta > 15%, (2C) chronological ordering | Deterministic threshold |
| **B3: Combined Normalized Rules** | All available signals at the assigned mask level, with normalized identity match, relative weight drop > 15% or 3σ outlier, and pairwise chronological checks | Deterministic combined rule engine (`BaselineCombinedNormalized`) |
| **B4: Structured Evidence + Abstention** | All available signals at the assigned mask level, with instrument uncertainty incorporation (Δm ≤ 2σ → `INDISTINGUISHABLE`), authorized repackaging tare adjustment, and explicit `INSUFFICIENT_EVIDENCE` for missing checkpoints | TriNetra Phase 1 reconciliation engine |

> [!IMPORTANT]
> **Fair comparison rule:** For every case evaluated by B4 at a given visibility mask, baselines B1–B3 must receive **exactly the same evidence visibility mask**. No baseline may receive more or less information than any other for the same comparison.

### 6.3 Evidence Visibility Masks

| Mask | Evidence Available | Representing |
|:---:|---|---|
| Mask 0 | Raw customer claim text only | Current industry practice (complaint queue) |
| Mask 1 | Warehouse receiving scan only (CP₅) | Single-endpoint inspection |
| Mask 2 | Supplier dispatch (CP₁) + Warehouse receiving (CP₅) | Forward-reverse endpoint comparison |
| Mask 3 | Complete custody chain (CP₁ → CP₂ → CP₃ → CP₄ → CP₅) | Full handover continuity |

### 6.4 Evaluation Metrics

| Metric | Definition | What It Tests |
|---|---|---|
| **Decision Accuracy** | Proportion of cases correctly resolved against ground truth | Overall correctness |
| **Appropriate Abstention Rate** | Proportion of `INDISTINGUISHABLE`/missing-data cases correctly assigned `REVIEW` | Uncertainty calibration |
| **False Hold Rate (Type I)** | Proportion of legitimate returns falsely flagged as tampered | Consumer protection |
| **Missed Change Rate (Type II)** | Proportion of changed/substituted units erroneously passed | Operational risk |
| **Inter-Rater Agreement** | Fleiss' κ across 3 reviewers at each mask level | Reviewer consistency |
| **Review Duration** | Elapsed time per case (seconds) | Operational burden |

---

## 7. Study D: Operational Feasibility Sensitivity Model

### 7.1 Scope Limitation

> [!WARNING]
> Study D is a **sensitivity analysis using assumed parameter values**, not an empirical cost-benefit analysis. It does not produce claims about real-world monetary savings, actual delivery-agent compliance, or operational ROI. All parameters are sensitivity inputs to be varied across a grid.

### 7.2 Sensitivity Parameter Grid

All values below are **assumptions for sensitivity analysis**, not empirical estimates:

| Parameter | Assumed Range | Source/Basis |
|---|---|---|
| Courier wage rate | ₹1.50 – ₹2.50/minute | **UNSOURCED ASSUMPTION** — requires external industry data |
| Capture time at doorstep | 5s / 15s / 45s | Experimental design (timed during Study B) |
| Reviewer adjudication time | Measured during Study C | Empirical from Study C |
| Dispute parcel value tier | < ₹1,000 / ₹1,000–5,000 / ₹5,000–25,000 / > ₹25,000 | **ASSUMPTION** — based on typical Indian e-commerce price ranges |
| Frontline compliance rate | 50% / 75% / 90% / 100% | **ASSUMPTION** — no empirical basis from this study |
| Dispute escalation rate | 2% / 5% / 10% | **ASSUMPTION** — no empirical basis from this study |
| Consumer commission penalty range | ₹5,000 – ₹25,000 | Observed in 4 legal cases (specific to those cases, not generalizable) |

### 7.3 Output

The sensitivity model produces **conditional break-even curves** showing: *"If the courier wage rate is X, and the compliance rate is Y, and the dispute escalation rate is Z, then the break-even parcel value for implementing handover telemetry is W."*

These curves inform future decisions but do not constitute evidence of operational viability.

---

## 8. Mandatory Governance, Integrity & Anti-Recurrence Rules

1. **Zero Public Narrative Scraping:** No customer complaints from social media, forums, or consumer review portals may be ingested, labeled, or presented as empirical ground truth.
2. **Physical Data Integrity:** Every row in `physical_observations.csv` must correspond to a verified physical item with verifiable instrument asset tags.
3. **Ground-Truth Blinding:** Ground truth stored in separate restricted file, never exposed to inference pipelines.
4. **No Synthetic F1 Inflation:** Unit/integration test results must never be cited as empirical research findings.
5. **No Claims of Fraudulent Intent:** The research classifies observable physical discrepancies and evidence gaps. It does not label individuals as fraudsters.
6. **No Nationwide Generalization:** Results from a 60-unit mock trial cannot be generalized to Indian e-commerce at scale.
7. **No Monetary Savings Claims:** Study D sensitivity outputs are conditional projections, not validated savings estimates.
