# TriNetra AI: Reviewer Calibration Case Pack (Cases C01–C10)

> **Document Type:** Reviewer-Facing Adjudication Materials & Case Pack  
> **Protocol Version:** 2.5.0  
> **Evaluation Mode:** Standardized Text-Based Rubric & Evidence Scenario Pack  
> **Target Audience:** Reviewers $R_1, R_2, R_3, R_4$  
> **Target Gate:** Gate E-3 Reviewer Calibration Trial (Rubric & Agreement Calibration)  
> **Session Status:** PENDING EXECUTION  

---

## 1. Reviewer Instructions & Calibration Objectives

Welcome to the TriNetra AI Adjudication Calibration Session. 

In this session, you will independently evaluate **10 benchmark return cases** ($C_{01} - C_{10}$). This calibration is a **text-based rubric and inter-reviewer agreement calibration** designed to:
1. Verify that all four reviewers interpret the five-layer adjudication taxonomy consistently;
2. Evaluate multi-rater agreement across raters on standardized case facts and evidence descriptions;
3. Establish whether reviewers appropriately abstain when evidence is ambiguous or degraded.

> [!NOTE]
> **Scope Boundary:** This calibration evaluates rubric understanding and inter-reviewer agreement on standardized case descriptions; it does **not** validate visual-interface proficiency or interactive UI tool handling. A separate, unscored interface familiarization step using non-experimental dummy walkthroughs will be conducted before the main trial sessions.

Your objective is to review the case facts, photographic descriptions, and scale weight trajectory data for each case, and submit your independent evaluative assessment.

> [!IMPORTANT]
> **INDEPENDENT EVALUATION:**  
> Complete all 10 cases independently without consulting other reviewers. Do not guess; if the evidence is genuinely ambiguous or photographically corrupted, use the appropriate abstention option.

---

## 2. Standardized Adjudication Form Fields

For each case, record your evaluation in [`calibration_ratings_template.csv`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/TriNetra_Mobile/research/reviewed_v2/calibration_ratings_template.csv):

### Field 1: Attribution Assessment ($\mathcal{A}$)
Select exactly one mutually exclusive attribution option:
- `ATTR_CONFIRMED_LEGITIMATE`: Package, factory seals, and serials confirmed intact and authentic across all checkpoints.
- `ATTR_STAGE_FORWARD_TRANSIT`: Evidence isolates discrepancy origin to forward transport between seller hub ($CP_1$) and delivery ($CP_2$).
- `ATTR_STAGE_DOORSTEP_DELIVERY`: Evidence isolates discrepancy origin to forward doorstep delivery handover at $CP_2$.
- `ATTR_STAGE_CONSUMER_CUSTODY`: Evidence isolates discrepancy origin to consumer custody between delivery ($CP_2$) and return pickup ($CP_3$).
- `ATTR_STAGE_REVERSE_TRANSIT`: Evidence isolates discrepancy origin to reverse transit between return pickup ($CP_3$) and warehouse intake ($CP_4$).
- `ATTR_STAGE_OTHER_OUTSIDE_SCOPE`: Evidence indicates discrepancy originated outside the observable handovers (e.g. factory defect before $CP_1$).
- `ATTR_ABSTAIN_INDISTINGUISHABLE`: Physical evidence is ambiguous; equally consistent with two or more discrepancy stages.
- `ATTR_ABSTAIN_DEGRADED`: Camera capture is underexposed, blurry, occluded, or digital scale failed ($0.0\text{g}$).

### Field 2: Operational Decision ($\mathcal{D}$)
Select exactly one operational platform business action:
- `DEC_APPROVE_REFUND`: Release customer refund immediately.
- `DEC_REJECT_REFUND`: Reject refund claim; flag account for return tampering/fraud.
- `DEC_HOLD_INVESTIGATION`: Place claim on 72-hour investigative hold; request field agent re-inspection.
- `DEC_CHARGEBACK_CARRIER`: Release customer refund; initiate formal 3PL carrier liability chargeback.
- `DEC_CHARGEBACK_VENDOR`: Initiate supplier/vendor chargeback.

### Field 3: Reviewer Confidence Score
Rate your subjective certainty from `1` (Very Low / Ambiguous) to `5` (Very High / Conclusive Proof).

### Field 4: Free-Text Justification
Provide a concise 1–2 sentence factual explanation citing specific visual features and scale weight deltas.

---

## 3. The 10 Calibration Case Evidence Files ($C_{01} - C_{10}$)

### Case C01: Return Tracking ID `CASE-CAL-01`
- **Product Category:** Smartphone Flagship X1 (Nominal product: 189.0g, Nominal tare: 116.0g, Total nominal: 305.0g).
- **Physical Sensory Observations:**
  - Checkpoint 1 ($CP_1$, Seller Dispatch): Outer carton pristine, factory holographic seal intact. Scale weight: **305.1g**. SHA-256 verified.
  - Checkpoint 2 ($CP_2$, Forward Doorstep OBD): Primary box intact, seal unbroken, barcode verified. Scale weight: **305.0g**.
  - Checkpoint 3 ($CP_3$, Return Pickup Handover): Return flyer bag sealed, primary box seals intact. Scale weight: **305.1g**.
  - Checkpoint 4 ($CP_4$, Warehouse Receiving): Carton intact, manufacturer seal unbroken, weight verified: **305.0g**.
- **Interface Flags:** Automated tare curve is flat ($\Delta w \in [-0.1\text{g}, +0.1\text{g}]$). No anomaly flags triggered.

---

### Case C02: Return Tracking ID `CASE-CAL-02`
- **Product Category:** Smartphone Flagship X1 (Total nominal: 305.0g).
- **Physical Sensory Observations:**
  - Checkpoint 1 ($CP_1$): Dispatched in merchant-branded poly flyer bag. Weight: **305.1g**.
  - Transit Hub Log: Courier transit scan logs outer flyer scuff during sortation; outer bag replaced with standard authorized carrier flyer bag.
  - Checkpoint 2 ($CP_2$): Delivered in carrier replacement flyer bag. Inner primary box inspected: factory seals 100% intact. Weight: **308.2g** (+3.1g heavier flyer bag material).
  - Checkpoint 3 ($CP_3$): Customer returns in carrier flyer bag. Primary box holographic seal intact. Weight: **308.1g**.
  - Checkpoint 4 ($CP_4$): Warehouse receiving verifies carrier re-bagging barcode, intact inner box seals, and authentic device inside. Weight: **308.3g**.
- **Interface Flags:** Tare curve step-shift at hub (+3.2g) matches carrier flyer replacement log. Inner seals intact.

---

### Case C03: Return Tracking ID `CASE-CAL-03`
- **Product Category:** Smartphone Flagship X1 (Total nominal: 305.0g).
- **Physical Sensory Observations:**
  - Checkpoint 1 ($CP_1$): Pristine outer box, seal intact. Scale weight: **305.1g**.
  - Checkpoint 2 ($CP_2$): Delivery photo shows carton top-right corner crushed inward by 35mm with deep compression crease. Manufacturer seal remains intact. Scale weight: **305.0g**.
  - Checkpoint 3 ($CP_3$): Customer returns unopened unit. Box presents identical corner crush. Seal intact. Scale weight: **305.1g**.
  - Checkpoint 4 ($CP_4$): Warehouse intake confirms package has corner crush from transit; seals unbroken. Scale weight: **305.0g**.
- **Interface Flags:** Synchronized visual delta highlights structural crease present at $CP_2, CP_3, CP_4$, absent at $CP_1$. Weights stable.

---

### Case C04: Return Tracking ID `CASE-CAL-04`
- **Product Category:** Smartphone Midrange M2 (Total nominal: 285.0g).
- **Physical Sensory Observations:**
  - Checkpoint 1 ($CP_1$): Dispatched intact, seal unbroken. Scale weight: **285.1g**.
  - Checkpoint 2 ($CP_2$): Delivery agent photo reveals severe edge shear tear and corner impact on carton base. Factory seal intact. Scale weight: **285.0g**.
  - Checkpoint 3 ($CP_3$): Customer handover photo documents identical bottom edge tear. Factory seal intact. Scale weight: **285.1g**.
  - Checkpoint 4 ($CP_4$): Warehouse receiving photo verifies base impact damage. Scale weight: **285.1g**.
- **Interface Flags:** Automated visual comparison flags perimeter tear appearing at $CP_2$.

---

### Case C05: Return Tracking ID `CASE-CAL-05`
- **Product Category:** Smartphone Flagship X1 (Dispatched model nominal: 305.0g).
- **Physical Sensory Observations:**
  - Checkpoint 1 ($CP_1$): Flagship X1 dispatched in sealed box. Barcode serial matches invoice. Scale weight: **305.1g**.
  - Checkpoint 2 ($CP_2$): Forward delivery OBD photo shows delivery agent handing over a box bearing barcode for budget model B3. Scale weight at doorstep: **252.0g** ($\Delta w = -53.1\text{g}$).
  - Checkpoint 3 ($CP_3$): Customer return pickup photo shows budget model B3 box. Scale weight: **252.1g**.
  - Checkpoint 4 ($CP_4$): Warehouse receives budget model B3. Scale weight: **251.9g**.
- **Interface Flags:** High-severity weight drop anomaly ($\Delta w = -53.1\text{g}$) and model barcode mismatch triggered at $CP_2$.

---

### Case C06: Return Tracking ID `CASE-CAL-06`
- **Product Category:** Smartphone Flagship X1 (Total nominal: 305.0g).
- **Physical Sensory Observations:**
  - Checkpoint 1 ($CP_1$): Factory seal intact, serial verified. Scale weight: **305.1g**.
  - Checkpoint 2 ($CP_2$): Delivered intact at doorstep; factory seal unbroken. Scale weight: **305.0g**.
  - Checkpoint 3 ($CP_3$): Pickup photo reveals manufacturer holographic seal sliced open and resealed with generic clear scotch tape. Scale weight: **210.0g** ($\Delta w = -95.0\text{g}$).
  - Checkpoint 4 ($CP_4$): Warehouse unboxing confirms handset extracted; empty accessories tray inside. Scale weight: **209.8g**.
- **Interface Flags:** Visual delta flags tape change at $CP_3$. Tare curve indicates 95.0g weight loss during customer custody ($CP_2 \to CP_3$).

---

### Case C07: Return Tracking ID `CASE-CAL-07`
- **Product Category:** Smartphone Midrange M2 (Total nominal: 285.0g).
- **Physical Sensory Observations:**
  - Checkpoint 1 ($CP_1$): Dispatched intact, seal intact. Scale weight: **285.1g**.
  - Checkpoint 2 ($CP_2$): Delivered intact, seal unbroken. Scale weight: **285.1g**.
  - Checkpoint 3 ($CP_3$): Pickup photo shows tamper seal cut and covered with wide brown packing tape. Scale weight: **322.0g** ($\Delta w = +36.9\text{g}$).
  - Checkpoint 4 ($CP_4$): Warehouse intake confirms seal broken; unboxing reveals dense ceramic tile insert. Scale weight: **321.8g**.
- **Interface Flags:** Automated weight delta anomaly flag (+36.9g excess) triggered at $CP_3$ return pickup.

---

### Case C08: Return Tracking ID `CASE-CAL-08`
- **Product Category:** Smartphone Flagship X1 (Total nominal: 305.0g).
- **Physical Sensory Observations:**
  - Checkpoint 1 ($CP_1$): Dispatched intact. Scale weight: **305.1g**.
  - Checkpoint 2 ($CP_2$): Delivered intact at doorstep. Scale weight: **305.0g**.
  - Checkpoint 3 ($CP_3$): Sealed return flyer handed over by customer. Flyer intact, tamper tape unbroken. Scale weight: **305.1g**.
  - Checkpoint 4 ($CP_4$): Warehouse intake photo shows bottom seam of poly flyer slit cleanly with razor and resealed with rough brown logistics tape. Handset missing. Scale weight: **140.0g** ($\Delta w = -165.1\text{g}$).
- **Interface Flags:** Visual delta detects flyer slit and brown tape replacement at $CP_4$ absent at $CP_3$. Weight drops 165.1g during reverse transit ($CP_3 \to CP_4$).

---

### Case C09: Return Tracking ID `CASE-CAL-09`
- **Product Category:** Smartphone Flagship X1 (Total nominal: 305.0g).
- **Physical Sensory Observations:**
  - Checkpoint 1 ($CP_1$): Dispatched intact. Scale weight: **305.1g**.
  - Checkpoint 2 ($CP_2$): Delivered intact at doorstep. Scale weight: **305.0g**.
  - Checkpoint 3 ($CP_3$): Return pickup photo was taken in darkness ($<10\text{ lux}$), exhibiting severe motion blur; seal area completely black/unreadable. Courier digital scale displays `ERR` / `0.0g`.
  - Checkpoint 4 ($CP_4$): Warehouse receives package with broken tamper seal and missing phone. Scale weight: **212.0g**.
- **Interface Flags:** Quality alert: $CP_3$ capture corrupted; zero weight logged; lux $<10$. Transition between $CP_2$ and $CP_4$ cannot be isolated.

---

### Case C10: Return Tracking ID `CASE-CAL-10`
- **Product Category:** Smartphone Flagship X1 (Total nominal: 305.0g).
- **Physical Sensory Observations:**
  - Checkpoint 1 ($CP_1$): Dispatched intact. Scale weight: **305.1g**.
  - Checkpoint 2 ($CP_2$): Delivered at doorstep. Smartphone unboxed for customer inspection. High camera flash specular reflection / glare covers center of screen. Scale weight: **305.0g**.
  - Checkpoint 3 ($CP_3$): Return pickup unboxed photo. High specular glare from overhead doorway light covers the identical screen area. Scale weight: **305.1g**.
  - Checkpoint 4 ($CP_4$): Warehouse diffuse LED lighting reveals 15mm hairline scratch across the center of the display screen. Scale weight: **305.0g**.
- **Interface Flags:** Visual inspection indicates glare occlusion at both $CP_2$ and $CP_3$. Physical evidence does not permit isolating whether the scratch existed prior to delivery or occurred during customer custody.
