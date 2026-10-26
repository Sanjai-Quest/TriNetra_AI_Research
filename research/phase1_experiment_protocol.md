# Phase 1 Experimental Research Protocol: Evidence Continuity Across Open Box Delivery, Reverse Logistics, and E-Commerce Disputes in India

> **Protocol Version:** 1.0.0 (Preregistration-Ready)  
> **Date:** 2026-10-24  
> **Study Status:** Design & Protocol Specification (Stage 2 Research Deliverable)  
> **Reference Schemas:** [`physical_observations_schema.md`](physical_observations_schema.md) and [`closest_work_matrix.csv`](research/closest_work_matrix.csv)  
> **Core Rule:** Strictly non-synthetic, unrigged evaluation. Evaluates physical observability, measurement uncertainty, and reviewer decision consistency.

---

## 1. Study Title & Core Research Questions

### 1.1 Working Title
*Evidence Continuity Across Open Box Delivery and Reverse Logistics: An India-Focused Experimental Study of E-Commerce Product Disputes*

### 1.2 Primary Research Question
> **Primary RQ:**  
> *"How does evidence captured at Open Box Delivery and subsequent return/warehouse handovers affect the ability to distinguish product or fulfilment errors, logistics handling changes and unresolved disputes in Indian e-commerce?"*

### 1.3 Sub-Questions (RQs)
- **RQ1 (Documentary Failure Taxonomy):** What failure modes are empirically documented in Indian official grievance data, marketplace OBD policies, and consumer commission decisions, and at which specific transaction handover do evidence gaps occur?
- **RQ2 (Minimal Evidentiary Fields):** Which specific physical telemetry fields (ordered SKU/variant, serial/IMEI where applicable, outer seal status, tare mass, repeated mass readings, timestamped images, handover acknowledgement) are necessary and sufficient to distinguish competing explanations for parcel discrepancies?
- **RQ3 (Reviewer Accuracy & Agreement):** Does a structured evidence packet with explicit abstention (`INDISTINGUISHABLE`) improve independent reviewers' agreement (Fleiss' $\kappa$) and accuracy against known ground truth compared with an unstructured complaint narrative or a basic checklist alone?
- **RQ4 (Operational Cost & Review Burden):** What is the net impact of multi-point handover telemetry on operator inspection time and operational cost under sensitivity-tested labor and dispute resolution rates?

---

## 2. Experimental Architecture: Four Linked Studies

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 EXPERIMENTAL ARCHITECTURE                              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  STUDY A: Documentary Evidence Map & Failure Mode Taxonomy                             │
│  • Primary sources: NCH Grievances, DCDRC Adjudicated Orders, Marketplace OBD Terms    │
│  • Output: Formal taxonomy of 8 canonical dispute scenarios                            │
│                                       │                                                │
│                                       ▼                                                │
│  STUDY B: Controlled Mock OBD-to-Warehouse Physical Trial                              │
│  • Cohort: 60 physical units across Electronics, Footwear, and Apparel                 │
│  • Handover traversal: Supplier -> Hub -> Doorstep OBD -> Return Pickup -> Warehouse   │
│  • Injections: Fulfilment errors, transit damage, packaging changes, indistinguishable │
│                                       │                                                │
│                                       ▼                                                │
│  STUDY C: Blinded Multi-Reviewer Adjudication Benchmark                                │
│  • Evaluators: Independent human reviewers & 4 baseline decision models                │
│  • Input: Visibility-masked evidence packets                                           │
│  • Metrics: Decision accuracy against known truth, Fleiss' Kappa, abstention rate      │
│                                       │                                                │
│                                       ▼                                                │
│  STUDY D: Economic & Review-Burden Sensitivity Model                                   │
│  • Variables: Inspection seconds, frontline compliance rate, dispute value tiers       │
│  • Output: Operational break-even curves for high-value e-commerce categories          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Study A: India-Focused Documentary Evidence Map

### 3.1 Objective
Construct an empirical taxonomy of documented e-commerce delivery and return failures in India, mapping where the chain of custody breaks down.

### 3.2 Data Sources & Inclusion Requirements
1. **Official Census Grievances:** National Consumer Helpline (NCH) annual grievance statistics from the Department of Consumer Affairs (e-commerce grievance census: 511,196 cases in 2025; PIB, 10 Sep 2026).
2. **Statutory Framework:** Consumer Protection (E-Commerce) Rules, 2020 and Consumer Protection (E-Commerce) (Amendment) Rules, 2026.
3. **Adjudicated Legal Case Orders:** Certified or accredited secondary legal reports from District Consumer Disputes Redressal Commissions (DCDRC) across Indian states (e.g., Central Mumbai CC/132/2022; Adilabad CC/24/2025; Kurnool CC/71/2025; Rangareddy CC/104/2025).
4. **Marketplace Operating Policies:** Published Terms and Conditions for Open Box Delivery (Flipkart OBD Terms, 2026) and Return Policies (Amazon India, Myntra, Ajio).

### 3.3 Case Coding Methodology
Each documented case is coded into a structured schema without inferring fraudulent intent:
- `case_id`: Official legal docket or policy reference number.
- `transaction_stage`: Forward Dispatch | Transit Hub | Doorstep Delivery (OBD) | Reverse Pickup | Warehouse Intake.
- `disputed_symptom`: Missing Component | Wrong Variant | Physical Damage | Counterfeit Substitution | Unrecorded State Change.
- `evidence_available`: Physical photos, unboxing videos, carrier scan logs, scale weight receipts.
- `evidence_missing`: Handover condition receipt, tare weight, serial number scan.
- `judicial_finding`: Deficiency in Service | Unfair Trade Practice | Dismissed.
- `legal_liability_attribution`: Seller | Marketplace Platform | Logistics Carrier | Customer.

---

## 4. Study B: Controlled Physical Experiment Protocol

### 4.1 Physical Unit Cohort
The trial utilizes **60 physical units** spanning 3 high-dispute merchandise categories in Indian e-commerce:

| Category | Unit Count | Target Items | Typical Mass Range | Primary Failure Vulnerabilities |
|---|:---:|---|:---:|---|
| **Consumer Electronics** | 20 | Smartphones, TWS Earbuds, Power Banks, Smartwatches | $150\text{g} - 800\text{g}$ | Model variant swaps, component stripping, accessory omission, unverified functional defects. |
| **Footwear** | 20 | Branded Sneakers, Running Shoes, Formal Leather Shoes | $600\text{g} - 1,400\text{g}$ | Size/variant confusion, sole wear, counterfeit substitution, packaging damage. |
| **Apparel & Accessories** | 20 | Boxed Watches, Branded Shirts, Sunglasses | $100\text{g} - 500\text{g}$ | Tag switching, cosmetic scratching, missing protective pouches, authorized repackaging. |

### 4.2 Standardized Measurement Instruments
- **Mass Measurements:** Calibrated digital precision scale with BLE interface, verified precision $\pm 0.1\text{g}$, calibration checked daily against standard test weights.
- **Visual Capture:** 12MP standardized smartphone camera under uniform 500-lux pack-station lighting.
- **Barcode / Optical Decode:** 2D DataMatrix and Code-128 handheld laser scanner reporting decode confidence scores.

### 4.3 Checkpoint Traversal Pipeline
Every physical unit traverses 5 sequential custody checkpoints:
1. **$CP_1$ (Supplier Dispatch / Outbound Pack-Station):** Initial gross mass, tare mass, serial/IMEI scan, intact tamper-evident seal photo.
2. **$CP_2$ (Logistics Hub Inbound):** Gross parcel mass, automated barcode scan, outer carton condition inspection.
3. **$CP_3$ (Doorstep Open Box Delivery):** Outer seal opening, visual component check, physical inspection (model, color, accessories), OTP verification simulation.
4. **$CP_4$ (Reverse Return Pickup):** Doorstep return pickup, physical condition classification (`INTACT`, `REPACKAGED`, `OPENED`, `DAMAGED`), pickup scale reading.
5. **$CP_5$ (Reverse Warehouse Receiving & Grading):** Intake weighing, seal integrity check, serial number audit, visual surface grading.

### 4.4 Controlled Experimental Injections ($n=60$)

The 60 cases are partitioned into 8 precisely controlled scenario types:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        60 CONTROLLED PHYSICAL TRIAL SCENARIOS                          │
├───────────────────────────────┬───────┬────────────────────────────────────────────────┤
│ Scenario Classification       │ Count │ Physical Condition Description                 │
├───────────────────────────────┼───────┼────────────────────────────────────────────────┤
│ 1. Clean Legitimate Journey   │  15   │ Authentic product, fully intact, zero changes   │
│ 2. Supplier Fulfilment Error  │   8   │ Wrong color/variant packed at CP1 (SKU error)  │
│ 3. Doorstep OBD Catch         │   7   │ Visible defect/missing item spotted at CP3     │
│ 4. Transit Damage             │   6   │ Crushed packaging and mass drop in transit CP2 │
│ 5. Post-Delivery Substitution │   8   │ Item swapped for counterfeit/dummy before CP4  │
│ 6. Legitimate Repackaging     │   6   │ Authorized carton change at CP2 (tare delta)   │
│ 7. Missing Custody Scans      │   5   │ CP2 or CP4 records omitted (evidence gap)      │
│ 8. Observationally Indist.    │   5   │ Modification within sensor noise (Δm < 2σ)     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Ground-Truth Status Specification
Ground truth is established *ex-ante* by the lead experimenter and held strictly private from evaluators:
- `LEGITIMATE`: Unit conforms to purchase order throughout journey.
- `FULFILMENT_ERROR`: Incorrect product, variant, or accessory packed prior to dispatch.
- `TRANSIT_DAMAGE`: Damage or loss occurring between dispatch and delivery.
- `POST_DELIVERY_CHANGE`: Substitution, wear, or component removal occurring between delivery and return pickup.
- `INDISTINGUISHABLE`: Physical discrepancy $\Delta m \le 2\sigma_{\text{instrument}}$ or legitimate repackaging indistinguishable from tampering without internal teardown.

---

## 5. Study C: Multi-Reviewer Adjudication Benchmark

### 5.1 Reviewer Cohort & Blinding
- **Human Evaluators:** 3 independent reviewers (trained in e-commerce dispute guidelines, blinded to ground truth and to other reviewers' scores).
- **Automated Baseline Models:** 4 algorithmic models evaluated on identical evidence payloads.

### 5.2 Competing Baselines Evaluated

1. **Baseline 1 (Unstructured Narrative / Complaint Only):**
   - Receives only raw consumer dispute text and stated return reason.
   - Evaluates whether text claims alone can distinguish physical truth (represents current practice in customer-service dispute queues).
2. **Baseline 2 (Single-Signal Diagnostic Probes):**
   - *Probe 2A (Identity Only):* Evaluates SKU string match only.
   - *Probe 2B (Weight Only):* Evaluates gross mass drop $> 15\%$.
   - *Probe 2C (Timeline Only):* Evaluates chronological event ordering.
3. **Baseline 3 (Combined Normalized Rules Model - `BaselineCombinedNormalized`):**
   - Applies normalized identity match, relative weight drop ($> 15\%$) or 3-sigma statistical outlier, and pairwise chronological sequence checks across checkpoints.
4. **Baseline 4 (Structured Evidence Continuity & Abstention Engine - TriNetra Phase 1):**
   - Ingests multi-point evidence packets conforming to [`physical_observations_schema.md`](physical_observations_schema.md).
   - Incorporates instrument uncertainty: if $|\Delta m| \le 2 \sigma_{\text{instrument}}$, explicitly returns `INDISTINGUISHABLE`.
   - Incorporates authorized repackaging adjustments: deducts known tare mass variations.
   - If critical handover checkpoints are absent, returns `INSUFFICIENT_EVIDENCE`.

### 5.3 Visibility Masking
To prevent information leakage, reviewers and models receive strictly masked evidence:
- **Mask 0 (Zero Telemetry):** Raw customer claim text only.
- **Mask 1 (Single Point):** Warehouse receiving scan only ($CP_5$).
- **Mask 2 (Forward & Reverse Endpoints):** Supplier dispatch ($CP_1$) + Warehouse receiving ($CP_5$).
- **Mask 3 (Full Handover Continuity):** Complete custody packet ($CP_1 \to CP_2 \to CP_3 \to CP_4 \to CP_5$).

### 5.4 Evaluation Metrics
1. **Decision Accuracy Against Ground Truth:** Proportion of correctly resolved cases across `LEGITIMATE`, `FULFILMENT_ERROR`, `TRANSIT_DAMAGE`, and `POST_DELIVERY_CHANGE`.
2. **Appropriate Abstention Rate:** Proportion of indistinguishable and missing-data cases correctly classified as `INDISTINGUISHABLE` or `INSUFFICIENT_EVIDENCE` (rather than forced into false positive or false negative errors).
3. **Inter-Rater Agreement:** Fleiss' Kappa ($\kappa$) and pairwise Cohen's Kappa across the 3 independent human reviewers.
4. **False Hold Rate (Alpha Error):** Proportion of legitimate returns falsely flagged as tampered.
5. **Missed Substitution Rate (Beta Error):** Proportion of substituted or damaged units erroneously passed as legitimate.
6. **Review Duration:** Elapsed adjudication time per case in seconds.

---

## 6. Study D: Operational Cost & Sensitivity Model

### 6.1 Cost Model Formulation
The net operational impact ($\Delta C$) of implementing handover telemetry is formalized as:

$$\Delta C = \sum_{i=1}^{N} \left( C_{\text{capture}}(t_i) + C_{\text{review}}(r_i) \right) - \left( S_{\text{fraud}} + S_{\text{dispute\_legal}} + S_{\text{handling}} \right)$$

Where:
- $C_{\text{capture}}(t_i) = t_i \cdot w_{\text{courier}}$: Frontline capture cost, where $t_i$ is extra seconds at doorstep/handover and $w_{\text{courier}}$ is courier wage rate ($\approx ₹1.50 - ₹2.50/\text{minute}$).
- $C_{\text{review}}(r_i) = r_i \cdot w_{\text{analyst}}$: Reviewer adjudication cost per disputed parcel.
- $S_{\text{fraud}}$: Recovered merchandise value from intercepted product substitutions.
- $S_{\text{dispute\_legal}}$: Avoided consumer commission penalties and legal compensation costs (e.g., avoided ₹10,000–₹25,000 awards under CPA 2019).
- $S_{\text{handling}}$: Avoided secondary handling, reverse freight, and restocking friction.

### 6.2 Sensitivity Parameter Grid
The cost-benefit model is evaluated across:
- **Dispute Parcel Value:** Tier 1 ($< ₹1,000$), Tier 2 ($₹1,000 - ₹5,000$), Tier 3 ($₹5,000 - ₹25,000$), Tier 4 ($> ₹25,000$).
- **Capture Duration ($t_i$):** 5 seconds (barcode + tare mass only) vs 15 seconds (photo + seal inspection) vs 45 seconds (full OBD unboxing).
- **Frontline Compliance Rate:** $50\%$, $75\%$, $90\%$, $100\%$.
- **Dispute Escalation Rate:** $2\%$, $5\%$, $10\%$ of returned orders.

---

## 7. Mandatory Governance, Integrity & Anti-Recurrence Rules

To permanently prevent recurrence of the audit failures identified in Phase 0 (Findings F-01 to F-08):
1. **Zero Public Narrative Scraping:** No customer complaints from social media, forums, or consumer review portals may be ingested, labeled, or passed as empirical ground truth.
2. **Physical Data Integrity:** Every row in `physical_observations.csv` must correspond to a verified physical item in the physical cohort, with verifiable instrument asset tags.
3. **Ground-Truth Blinding:** Ground truth must be stored in a separate, encrypted/restricted file `ground_truth_private.csv` accessible only to the audit supervisor, never exposed to inference pipelines.
4. **No Synthetic F1 Inflation:** Unit/integration tests (such as the 15 tests in `synthetic_disputes.csv`) must never be cited as empirical research findings.
5. **No Claims of Fraudulent Intent:** The research classifies observable physical discrepancies and evidence gaps. It does not label individuals as fraudsters or deduce subjective legal intent.
