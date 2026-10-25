# TriNetra Physical Observations Schema & Protocol Specification

> **Document Version:** 1.0.0  
> **Date:** 2026-10-23  
> **Status:** Implementation Baseline (Remediation C-15, Section 6)  
> **Reference:** [remediation_plan.md](file:///C:/Users/mitsu/.gemini/antigravity-ide/brain/2eee12ce-65d9-4965-a60d-e0760175bfa7/remediation_plan.md) §6.1–6.3  

---

## 1. Overview and Research Objective

The primary Phase 1 research study investigates **pre-delivery package verification at supplier, warehouse, and fulfilment checkpoints**. It evaluates how:
- Measurement uncertainty (scale tolerance, instrument drift, precision limitations)
- Permitted packaging modifications (re-boxing, accessory bundling, tape changes)
- Checkpoint record inconsistencies (missing scans, unsynchronized clocks)
- Observational indistinguishability

impact the ability to distinguish authentic physical packages from tampered, altered, or fraudulent consignments.

This document establishes the official schema and measurement protocol for empirical physical observations (`physical_observations.csv`).

---

## 2. Dataset Schema: `physical_observations.csv`

Every physical inspection event recorded across the supply chain must conform to this schema.

| Column | Type | Nullable | Permitted Values / Format | Description |
|---|---|---|---|---|
| `observation_id` | UUID | No | UUIDv4 (e.g., `550e8400-e29b-41d4-a716-446655440000`) | Globally unique identifier for this physical observation event. |
| `unit_id` | String | No | Ref: `serialized_units.unit_id` (e.g., `UNIT-TEST-001`) | Serialized logistics unit identifier tracked through the chain. |
| `checkpoint_type` | String | No | `SUPPLIER_DISPATCH`, `WAREHOUSE_INBOUND`, `WAREHOUSE_PICKING`, `OUTBOUND_DISPATCH`, `CARRIER_HUB`, `DELIVERY_HANDOFF`, `RETURN_RECEIVING` | Canonical checkpoint location type in the custody chain. |
| `checkpoint_location` | String | No | ISO / Facility code (e.g., `BOM-WH-02`, `DEL-HUB-01`) | Unique code of the physical inspection station. |
| `operator_id` | String | No | String (e.g., `OP_9021`) | Anonymized identifier of the station operator. |
| `timestamp_utc` | String | No | ISO-8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`) | High-precision observation timestamp. |
| `instrument_id` | String | No | String (e.g., `SCALE_BLE_04`) | Hardware device serial / asset tag. |
| `instrument_type` | String | No | `BLE_SCALE`, `BARCODE_SCANNER`, `VISION_CAMERA`, `MANUAL_CALIPER`, `MANUAL_ENTRY` | Sensor or input modality used for the measurement. |
| `instrument_precision` | Float | No | Numeric (e.g., `0.5` for ±0.5g) | Stated measurement uncertainty limit of the instrument. |
| `instrument_last_cal` | String | Yes | ISO-8601 Date (`YYYY-MM-DD`) | Date of most recent sensor calibration check. |
| `raw_mass_grams` | Float | Yes | Numeric > 0 (e.g., `452.3`) | Gross measured mass reading from scale (null if instrument not a scale). |
| `repeated_readings` | JSON | Yes | JSON array of floats (e.g., `[452.1, 452.4, 452.3]`) | Minimum 3 repeated weighings to establish empirical variance. |
| `tare_mass_grams` | Float | Yes | Numeric ≥ 0 (e.g., `45.0`) | Measured tare weight of packaging material if evaluated separately. |
| `net_mass_grams` | Float | Yes | Numeric > 0 | Net product mass (`raw_mass_grams - tare_mass_grams`). |
| `packaging_state` | String | No | `ORIGINAL_SEALED`, `REPACKAGED`, `OPENED`, `DAMAGED_CRUSHED`, `WATER_DAMAGED`, `UNKNOWN` | Visual packaging integrity classification. |
| `packaging_change_reason` | String | Yes | String (e.g., `accessory_kit_added`, `outer_carton_reinforced`) | Authorized operational reason for legitimate packaging change. |
| `seal_status` | String | No | `INTACT`, `TAMPER_EVIDENT_VOID`, `BROKEN_MISSING`, `NOT_APPLICABLE` | Security tape / seal status. |
| `outer_condition` | String | No | `NORMAL`, `CRUSHED`, `WET`, `TORN`, `PUNCTURED`, `OTHER` | Physical parcel exterior state. |
| `barcode_value` | String | Yes | String | Raw scanned barcode / DataMatrix content. |
| `barcode_scan_confidence` | Float | Yes | Float in range `[0.0, 1.0]` | Hardware/computer-vision decode confidence score. |
| `serial_observed` | String | Yes | String | Serial number recorded on packaging label or device. |
| `imei_observed` | String | Yes | String | 15-digit IMEI if applicable for cellular equipment. |
| `photo_evidence_path` | String | Yes | Relative path (e.g., `evidence/photos/obs_901.jpg`) | Audit photo captured during inspection. |
| `evidence_completeness` | String | No | `COMPLETE`, `PARTIAL`, `INSUFFICIENT` | Custody completeness flag for the observation. |
| `ground_truth_status` | String | No | `LEGITIMATE`, `INCONSISTENT`, `INDISTINGUISHABLE`, `NOT_ASSESSED` | Independent audit verdict. **Never populated by the detector.** |
| `ground_truth_source` | String | Yes | `AUDITOR_PHYSICAL_INSPECTION`, `MANUFACTURER_BENCH_TEST`, `POST_MORTEM_DISASSEMBLY` | Provenance of ground-truth verdict. |
| `ground_truth_assessor` | String | Yes | String (e.g., `AUDITOR_ALPHA`) | Independent assessor ID (disjoint from operator_id). |
| `ground_truth_timestamp` | String | Yes | ISO-8601 UTC | Timestamp when audit verdict was sealed. |
| `ground_truth_notes` | String | Yes | Text string | Explanatory rationale for ground-truth classification. |

---

## 3. Observational Indistinguishability: First-Class Ground Truth

A critical contribution of this research framework is defining cases that **cannot be resolved** from available observational signals:

$$\Delta m = |m_{\text{observed}} - m_{\text{baseline}}| \le 2 \cdot \sigma_{\text{instrument}}$$

When a substitution or alteration produces physical discrepancies within instrument noise bounds, or when authorized repackaging mimics unauthorized tampering, the ground truth is strictly:

$$\text{ground\_truth\_status} = \mathbf{INDISTINGUISHABLE}$$

> [!IMPORTANT]
> A decision engine that flags an indistinguishable case as a confident anomaly or confident legitimate state is exhibiting false precision. Flagging uncertainty in these cases is the correct scientific outcome.

---

## 4. Controlled Physical Experiment Protocol (§6.2)

To collect empirical data conforming to this schema, researchers must follow the controlled trial protocol:

1. **Unit Cohort:** Minimum 50 physical units spanning ≥ 3 distinct merchandise categories:
   - Consumer Electronics (smartphones, earbuds, power banks)
   - Footwear (sneakers, boots with varied packaging mass)
   - Apparel & Accessories (boxed watches, garments)
2. **Checkpoint Traversal:** Every unit traverses ≥ 3 sequential checkpoints:
   - Checkpoint 1: Outbound Dispatch
   - Checkpoint 2: Courier Hub Sorting
   - Checkpoint 3: Inbound / Return Receiving
3. **Repeated Measurement:** At each checkpoint, record $\ge 3$ consecutive weight readings (`repeated_readings`) to quantify sensor noise.
4. **Legitimate Variations:** Introduce at least 5 authorized packaging variations across control units:
   - Packaging material change (bubble wrap $\to$ air pillows)
   - Authorized repackaging due to carton damage
   - Legitimate accessory bundling (promotional item added)
5. **Introduced Physical Inconsistencies:** Across $\ge 20$ test units, introduce verified anomalies:
   - Weight drop via accessory omission ($\Delta m \in [5\text{g}, 150\text{g}]$)
   - Barcode label swap with adjacent SKU
   - Broken tamper-evident seal with cosmetic re-gluing
6. **Blinded Ground Truth:** The ground-truth auditor (`ground_truth_assessor`) assigns labels independently of and blinded to the decision engine's predictions.
7. **Deliberate Indistinguishability Injections:** Minimum 10 cases must feature modifications whose magnitude is smaller than twice the sensor uncertainty ($\Delta m < 2 \sigma$).

---

## 5. Prohibited Data Sources (§6.3)

Under this schema, the following data are **strictly prohibited** and will be rejected by automated CI intake guards (`test_synthetic_label_guard.py`):
1. Consumer complaint narratives parsed for sentiment or keywords.
2. Template-generated synthetic weight values produced by software loops.
3. Invariant constant fields (e.g., hardcoded `evidence_missing=0`).
4. Re-labeled outputs of previous decision engine iterations.
