# TriNetra AI: Synthetic Dry-Run Case Pack (DRYRUN-01 to DRYRUN-10)

> **Document Status:** SYNTHETIC REHEARSAL FIXTURE — NOT HUMAN REVIEW DATA  
> **Classification:** Diagnostic Dry Run & Consistency Testing  
> **Target Audience:** Synthetic AI Reviewer Agents (Agent A, Agent B, Agent C, Agent D)  
> **Notice:** This document contains strictly synthetic cases designed exclusively to test AI classification consistency, rubric ambiguity, and pipeline mechanics. It does NOT use official calibration cases (C01–C10) or official experiment journeys (J01–J60), and must NOT be used to satisfy Gate E-3.

---

## Standardized Adjudication Rubric & Options

All reviewer agents must select exactly one Attribution Assessment ($\mathcal{A}$) and one Operational Decision ($\mathcal{D}$) from the official taxonomy:

### Attribution Assessment Categories ($\mathcal{A}$):
1. `ATTR_CONFIRMED_LEGITIMATE`: Package, factory seals, serials, and tare weight confirmed intact and authentic across all observable checkpoints; return is legitimate.
2. `ATTR_STAGE_FORWARD_TRANSIT`: Evidence isolates discrepancy origin to forward transport between seller hub ($CP_1$) and customer delivery handover ($CP_2$).
3. `ATTR_STAGE_DOORSTEP_DELIVERY`: Evidence isolates discrepancy origin to the forward delivery handover at customer doorstep ($CP_2$).
4. `ATTR_STAGE_CONSUMER_CUSTODY`: Evidence isolates discrepancy origin to consumer custody between delivery ($CP_2$) and return pickup ($CP_3$).
5. `ATTR_STAGE_REVERSE_TRANSIT`: Evidence isolates discrepancy origin to reverse transit between return pickup ($CP_3$) and warehouse intake ($CP_4$).
6. `ATTR_STAGE_OTHER_OUTSIDE_SCOPE`: Evidence indicates discrepancy originated outside observable handovers (e.g., manufacturer/factory defect prior to $CP_1$).
7. `ATTR_ABSTAIN_INDISTINGUISHABLE`: Physical evidence is ambiguous or equally consistent with two or more discrepancy stages; impossible to isolate stage with certainty.
8. `ATTR_ABSTAIN_DEGRADED`: Camera capture is underexposed ($<15\text{ lux}$), blurred, occluded, or digital scale failed ($0.0\text{g}$) at a critical boundary.

### Operational Decision Categories ($\mathcal{D}$):
1. `DEC_APPROVE_REFUND`: Release customer refund immediately (return confirmed legitimate or platform liability).
2. `DEC_REJECT_REFUND`: Reject refund claim; flag account for return fraud / item substitution.
3. `DEC_HOLD_INVESTIGATION`: Place claim on 72-hour investigative hold; request field agent re-inspection or carrier inquiry (required for ambiguous/degraded cases).
4. `DEC_CHARGEBACK_CARRIER`: Release customer refund; initiate formal 3PL logistics carrier liability chargeback.
5. `DEC_CHARGEBACK_VENDOR`: Reject or reverse payout to seller/vendor due to pre-existing origin defect.

---

## Synthetic Cases

### Case DRYRUN-01: Wireless Over-Ear Headphones
- **Item & Declared Spec:** Audiophile Wireless Headphones (Nominal Net Weight: 250.0g, Packaging: 150.0g, Total Gross: 400.0g).
- **Customer Return Reason:** Buyer remorse ("Unwanted birthday gift, box unopened").
- **Checkpoint Evidence:**
  - **$CP_1$ (Seller Hub Dispatch):** Holographic tamper seal #H-4412 intact. Serial #WH-99201 verified. Calibrated digital scale: **400.2g**. High-resolution photo confirms pristine carton.
  - **$CP_2$ (Doorstep Delivery):** Recipient accepted. Seal #H-4412 intact. Scale reading: **400.1g**. Photo confirms no dents or edge crushing.
  - **$CP_3$ (Return Pickup Handover):** Courier doorstep pickup. Seal #H-4412 intact, zero tears. Scale reading: **400.0g**. Security outer bag #SB-101 sealed.
  - **$CP_4$ (Warehouse Intake):** Security outer bag #SB-101 intact. Seal #H-4412 verified intact under UV illumination. Scale reading: **400.1g**. Handset serial #WH-99201 confirmed authentic inside.

---

### Case DRYRUN-02: Rugged Outdoor Bluetooth Speaker
- **Item & Declared Spec:** Rugged Waterproof Bluetooth Speaker (Nominal Gross Weight: 620.0g).
- **Customer Return Reason:** "Received item crushed and damaged upon opening".
- **Checkpoint Evidence:**
  - **$CP_1$ (Seller Hub Dispatch):** Factory carton pristine. Tamper seal #BT-8812 intact. Digital scale: **620.4g**. Carton corners sharp.
  - **$CP_2$ (Doorstep Delivery):** Courier photo at doorstep reveals heavy corner impact crush, carton punctured on left flank with visible fluid staining from carrier van floor. Scale reading: **619.8g**. Courier log note: *"Carton dropped from conveyor belt during transit hub sort."*
  - **$CP_3$ (Return Pickup Handover):** Same crushed carton collected. Tamper seal intact. Scale reading: **619.5g**. Return tamper bag applied.
  - **$CP_4$ (Warehouse Intake):** Return tamper bag intact. Speaker grill bent inward matching puncture documented at $CP_2$. Scale reading: **619.7g**. Serial matches invoice.

---

### Case DRYRUN-03: Luxury Smartwatch
- **Item & Declared Spec:** Premium Smartwatch (Nominal Gross Weight: 280.0g).
- **Customer Return Reason:** "Delivery agent handed over wrong generic box; refused delivery on spot."
- **Checkpoint Evidence:**
  - **$CP_1$ (Seller Hub Dispatch):** Branded matte-black luxury packaging with security hologram #SW-3101. Serial #SW-8814. Digital scale: **280.5g**.
  - **$CP_2$ (Doorstep Delivery):** Doorstep handover photo captured by delivery courier shows a plain unbranded brown cardboard box with handwritten marker text instead of branded packaging. Hologram #SW-3101 absent. Portable scale reading: **198.0g** ($\Delta W = -82.5\text{g}$). Customer refused acceptance on spot. Courier completed return initiation.
  - **$CP_3$ (Return Pickup Handover):** N/A (Immediate rejection at $CP_2$; courier retained parcel in van).
  - **$CP_4$ (Warehouse Intake):** Brown box received. Inside: empty plastic casing and metal nut. Digital scale: **197.8g**.

---

### Case DRYRUN-04: Android Tablet 10-inch
- **Item & Declared Spec:** 10-inch Tablet (Handset: 460.0g, Packaging: 220.0g, Total Gross: 680.0g).
- **Customer Return Reason:** "Defective screen, will not turn on."
- **Checkpoint Evidence:**
  - **$CP_1$ (Seller Hub Dispatch):** Factory shrinkwrap sealed with micro-perforations. Holographic barcode #TB-5519. Digital scale: **680.2g**.
  - **$CP_2$ (Doorstep Delivery):** Handover photo shows shrinkwrap pristine, barcode #TB-5519 verified. Portable scale: **680.0g**. Customer signed OTP confirmation.
  - **$CP_3$ (Return Pickup Handover):** 5 days later. Return courier photo reveals factory shrinkwrap sliced open along side seam and resealed with standard transparent scotch tape. Portable scale reading: **440.0g** ($\Delta W = -240.0\text{g}$).
  - **$CP_4$ (Warehouse Intake):** Unsealed at intake bench. Handset extracted: genuine tablet missing; substituted with a dummy flat ceramic tile wrapped in bubble film. Serial label scraped off. Digital scale: **439.8g**.

---

### Case DRYRUN-05: High-Precision Camera Lens
- **Item & Declared Spec:** 50mm f/1.4 Camera Lens (Total Gross Weight: 510.0g).
- **Customer Return Reason:** "Autofocus motor sounds noisy."
- **Checkpoint Evidence:**
  - **$CP_1$ (Seller Hub Dispatch):** Branded lens box with security label #LN-7721 intact. Digital scale: **510.2g**.
  - **$CP_2$ (Doorstep Delivery):** Box pristine, label #LN-7721 intact. Scale: **510.1g**. Handed to customer.
  - **$CP_3$ (Return Pickup Handover):** Customer handed over original box. Label #LN-7721 intact. Digital scale: **510.0g**. Pickup agent enclosed package in tamper-evident security pouch #SEC-9904. Clear photograph of sealed pouch barcode #SEC-9904.
  - **$CP_4$ (Warehouse Intake):** Package arrived at central reverse logistics facility. Inspection reveals pouch #SEC-9904 has a razor slit along bottom heat-weld seam resealed with glue. Digital scale: **315.0g** ($\Delta W = -195.0\text{g}$). Inside carton: genuine lens missing; substituted with broken water tumbler and foam peanuts.

---

### Case DRYRUN-06: Backlit Mechanical Keyboard
- **Item & Declared Spec:** Mechanical Gaming Keyboard (Nominal Gross Weight: 1100.0g).
- **Customer Return Reason:** "Spacebar and Enter keys completely dead out of the box."
- **Checkpoint Evidence:**
  - **$CP_1$ (Seller Hub Dispatch):** Manufacturer tamper-evident round sticker intact. Barcode #KB-1044. Digital scale: **1102.0g**. Carton pristine.
  - **$CP_2$ (Doorstep Delivery):** Manufacturer sticker intact. Scale: **1101.5g**. Packaging pristine.
  - **$CP_3$ (Return Pickup Handover):** Manufacturer sticker carefully inspected; intact without disturbance. Scale: **1101.8g**. Outer carton pristine.
  - **$CP_4$ (Warehouse Intake):** Sticker intact. Scale: **1101.9g**. Intake technician opened box under camera: keyboard serial matches outer box and invoice. Hardware diagnosis: internal mainboard missing factory solder joint on switch rail (manufacturing soldering defect prior to packaging). Zero physical damage or tampering.

---

### Case DRYRUN-07: ANC Earbuds (Sensor-Degraded Low Lux)
- **Item & Declared Spec:** True Wireless Earbuds (Gross Weight: 145.0g).
- **Customer Return Reason:** "Left earbud stopped charging."
- **Checkpoint Evidence:**
  - **$CP_1$ (Seller Hub Dispatch):** Factory seal intact. Digital scale: **145.2g**. High-res crisp photo.
  - **$CP_2$ (Doorstep Delivery):** Factory seal intact. Digital scale: **145.0g**. Photo crisp.
  - **$CP_3$ (Return Pickup Handover):** Pickup photo taken inside dark unlit residential stairwell ($<3\text{ lux}$); image is completely underexposed, black, and unidentifiable. Handheld scale battery died; scale reading recorded as **0.0g** (error flag `ERR_SCALE_NO_READING`).
  - **$CP_4$ (Warehouse Intake):** Package received with outer seal torn. Scale reading: **95.0g** ($\Delta W = -50.0\text{g}$). Charging case present but earbuds missing inside.

---

### Case DRYRUN-08: Portable 2TB SSD (Sensor-Degraded Motion Blur)
- **Item & Declared Spec:** Portable Solid State Drive (Gross Weight: 180.0g).
- **Customer Return Reason:** "Drive not recognized by laptop."
- **Checkpoint Evidence:**
  - **$CP_1$ (Seller Hub Dispatch):** Tamper label intact. Digital scale: **180.1g**. Photo clear.
  - **$CP_2$ (Doorstep Delivery):** Courier photo exhibits extreme rotational motion blur (shutter speed $1/4\text{s}$ while walking); seal text and package edge completely smeared and illegible. Courier scale failed to connect via Bluetooth; recorded as **0.0g**.
  - **$CP_3$ (Return Pickup Handover):** Photo clear. Seal torn and taped. Scale: **110.0g**.
  - **$CP_4$ (Warehouse Intake):** Scale: **110.2g**. Inside box: SSD replaced with metal plate.

---

### Case DRYRUN-09: Action Camera (Specular Flash Glare Ambiguity)
- **Item & Declared Spec:** Waterproof 4K Action Camera (Gross Weight: 320.0g).
- **Customer Return Reason:** "Lens housing corner cracked."
- **Checkpoint Evidence:**
  - **$CP_1$ (Seller Hub Dispatch):** Transparent blister display box. Digital scale: **320.0g**. Pristine.
  - **$CP_2$ (Doorstep Delivery):** Doorstep photo taken with direct on-camera flash. Intense specular reflection and bright white flare completely cover top-right corner of camera housing. Scale: **320.1g**.
  - **$CP_3$ (Return Pickup Handover):** Doorstep return photo also taken with direct phone flash; identical bright white specular glare circle covers top-right corner. Scale: **320.0g**.
  - **$CP_4$ (Warehouse Intake):** Under diffuse studio LED lighting: hairline fracture discovered on top-right housing corner. Scale: **320.0g** (hairline crack causes zero weight delta).
  - **Epistemic Note:** Physical crack is present, but because glare covered the exact fracture site at both $CP_2$ and $CP_3$, it is impossible to determine whether crack occurred during forward transit, delivery, or customer custody.

---

### Case DRYRUN-10: E-Ink Reader (Conflicting Scale Drift)
- **Item & Declared Spec:** 6-inch E-Reader (Gross Weight: 260.0g).
- **Customer Return Reason:** "Screen freeze."
- **Checkpoint Evidence:**
  - **$CP_1$ (Seller Hub Dispatch):** Factory seal intact. Digital scale: **260.2g**.
  - **$CP_2$ (Doorstep Delivery):** Handover photo shows sealed box with zero damage. Scale reading: **210.0g** ($\Delta W = -50.2\text{g}$).
  - **$CP_3$ (Return Pickup Handover):** Photo shows sealed box intact. Scale reading: **210.1g**.
  - **$CP_4$ (Warehouse Intake):** Package opened. Genuine reader intact, serial matches. Digital scale: **260.1g**.
  - **Maintenance Audit Note:** Service log for courier depot scale used at $CP_2$ and $CP_3$ indicates scale load cell was uncalibrated and drifted by exactly $-50.0\text{g}$ throughout that shift.
  - **Epistemic Note:** While weight showed delta $-50\text{g}$, the box remained sealed and device was intact at $CP_4$ with true weight $260.1\text{g}$.
