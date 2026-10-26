# Forensic Audit: Label Provenance, Target Leakage, and Data Fabrication Findings

**Audit Authority:** Senior Data Engineering & Research Reproducibility Engineer  
**Audit Scope:** TriNetra AI & TriNetra Mobile Codebase  
**Date of Audit:** October 2026  
**Status:** COMPLETE (Read-Only Phase 0 Investigation)

---

## 1. Executive Summary

This forensic audit investigates how datasets, ground-truth labels, collection pipelines, and evaluation metrics were produced across the TriNetra project. The investigation reveals a catastrophic breakdown in data integrity and research reproducibility within the legacy research and consumer complaint mining subsystems. 

The previous complaint-generation automation **systematically fabricated 1,050 dispute records** using hardcoded string templates and synthetic URL generators, while publishing academic reports claiming the dataset was *"100% authentic real-world customer complaints"* with *"0% synthetic data"* and *"zero hallucinated facts"*. 

Furthermore, downstream evaluation pipelines exhibit **severe label circularity and target leakage**:
1. Synthetic physical telemetry (scale weights, altered SKUs, inverted timestamps) was manufactured directly from the complaint text to guarantee detection.
2. Single-dimensional baselines were artificially restricted to ensure TriNetra's multidimensional engine outperformed them by design.
3. Risk-scoring validation scripts hardcoded artificial buyer and seller histories to fabricate statistical correlations.
4. Validation scripts forged backend accuracy and response latencies when the backend server was offline.
5. In an attempt to demo the system, three fabricated complaint IDs were seeded into the current V3 logistics database, cross-contaminating the pre-delivery physical verification system.

Below is the exhaustive, evidence-backed breakdown of each finding with exact file, function, line, and column citations.

---

## 2. Finding 1: Fabricated Consumer Grievance Corpus Masquerading as Real Data

### 2.1 The Generation Mechanism of the "Original 271" Dataset
- **Affected File:** [`TriNetra_Mobile/TriNetra AI/xscrapper/xscrapper/complaint_mining/expand_master_dataset.py`](TriNetra%20AI/xscrapper/xscrapper/complaint_mining/expand_master_dataset.py)
- **Target File:** [`TriNetra_Mobile/datasets/customer_complaints_dataset.csv`](datasets/customer_complaints_dataset.csv) (271 rows)

#### Citation & Code Evidence:
In `expand_master_dataset.py`, lines 39–118 define 4 template lists (`fashion_templates`, `electronics_templates`, `beauty_templates`, `general_templates`) comprising fewer than 30 distinct base grievance narratives. 

Lines 120–174 then generate the dataset by cycling through these templates and appending random string variations:
```python
# expand_master_dataset.py: lines 139-146
variations = [
    f" Order reference #{100000+variation_id}. Please help resolve this issue urgently.",
    f" Case ID #{80000+variation_id}. Terrible experience with {brand} customer support.",
    f" Complaint registered. Disappointed with the service quality.",
    f" Order date: {(start_date + datetime.timedelta(days=variation_id%50)).strftime('%d %b %Y')}. Seeking immediate resolution.",
    f" Escalated to consumer court forum. Ticket #{50000+variation_id}.",
    f" Requesting refund or replacement immediately. Order #{20000+variation_id}."
]
full_text = text_base + random.choice(variations)
```

Lines 163–170 fabricate synthetic URLs using string interpolation:
```python
domain_map = {
    "Reddit": f"https://www.reddit.com/r/{brand}In/comments/c{variation_id:05d}/complaint/",
    "X (Twitter)": f"https://x.com/user_{variation_id}/status/178000000{variation_id:04d}",
    "LinkedIn": f"https://www.linkedin.com/posts/user_{variation_id}_complaint_activity_{7180000000+variation_id}",
    "Facebook": f"https://www.facebook.com/groups/consumercomplaints/posts/{8800000+variation_id}/",
    "Instagram": f"https://www.instagram.com/p/C5{variation_id:05d}/"
}
```

Line 127 reveals the starting state:
```python
curr_id = max([int(r["Complaint_ID"].replace("CMP_", "")) for r in existing_rows ...] or [48]) + 1
```
The script was used to fill the dataset up to 271 rows. Every single URL in `customer_complaints_dataset.csv` matches this exact generation formula. For example, row 111 and row 254 generated `https://www.reddit.com/r/D2C BrandIn/comments/c00114/complaint/` containing an impossible space in the URL because `brand` was `"D2C Brand"`.

### 2.2 The 1,050 Record Expansion Pipeline
- **Affected File:** [`TriNetra_Mobile/TriNetra AI/xscrapper/xscrapper/complaint_mining/build_trinetra_1000_corpus.py`](TriNetra%20AI/xscrapper/xscrapper/complaint_mining/build_trinetra_1000_corpus.py)
- **Target File:** [`TriNetra_Mobile/datasets/trinetra_real_complaints_expanded.csv`](datasets/trinetra_real_complaints_expanded.csv) (1,050 rows)

#### Citation & Code Evidence:
Lines 51–137 define 37 dispute templates in `DISPUTE_SCENARIOS`. 
Lines 139–150 define 10 synthetic URL prefix formats:
```python
SOURCE_PLATFORMS = [
    ("Reddit (r/LegalAdviceIndia)", "https://reddit.com/r/LegalAdviceIndia/comments/"),
    ("Reddit (r/Flipkart)", "https://reddit.com/r/Flipkart/comments/"),
    ...
    ("X / Twitter Public Dispute Thread", "https://x.com/consumer_dispute/status/"),
    ("LinkedIn Public Consumer Grievance", "https://linkedin.com/posts/grievance_")
]
```

Lines 274–348 cycle through these 37 templates to expand the preserved 271 rows to 1,050 rows:
```python
# build_trinetra_1000_corpus.py: lines 281-295
ord_num = 100000 + next_id
dt_offset = random.randint(0, 420)
c_date = base_date + timedelta(days=dt_offset)
date_str = c_date.strftime("%Y-%m-%d")
var_text = random.choice(variation_tails).format(ord=ord_num, dt=date_str)
full_text = text_base + var_text
url = f"{url_prefix}{next_id:05d}/dispute_{ord_num}"
likes = random.randint(3, 160)
replies = random.randint(1, 45)
```

### 2.3 False Claims of Authenticity in Reports
Despite 100% of these records being generated in Python loops:
1. In [`dataset_and_literature_engineering_report.md`](TriNetra%20AI/xscrapper/xscrapper/validation_report/dataset_and_literature_engineering_report.md) (lines 14, 75):
   > *"A multi-platform empirical dataset of 271 100% authentic real-world customer complaints across 5 major social/review channels... All legacy Bing noise has been completely purged."*
2. In [`trinetra_complaint_quality_report.md`](datasets/trinetra_complaint_quality_report.md) (lines 453, 509):
   > *"- Synthetic Data Flag: 0% synthetic (100% authentic dispute narratives)"*  
   > *"1. Zero Hallucinated Facts: Every record reflects authentic consumer complaints and real dispute patterns."*

---

## 3. Finding 2: Circular Ground Truth & Telemetry Injection

### 3.1 Mechanism of Fabrication
- **Affected File:** [`TriNetra_Mobile/TriNetra AI/phase-1/data/build_real_dataset.py`](TriNetra%20AI/phase-1/data/build_real_dataset.py)
- **Target Files:** [`real_complaint_cases.json`](TriNetra%20AI/phase-1/data/real_complaint_cases.json) and [`synthetic_evidence.csv`](TriNetra%20AI/phase-1/data/synthetic_evidence.csv)

The authors sought to benchmark their reconciliation engine on physical telemetry (weights, SKUs, and timestamps). Because consumer complaint posts on Reddit and Twitter do not contain warehouse scale readings, barcode scans, or carrier timestamps, the script manufactured them by parsing the synthetic text and injecting matching telemetry defects.

#### Code Evidence from `build_real_dataset.py`:
```python
# Lines 36-48: Map complaint type to conflict dimension
COMPLAINT_TO_CONFLICT = {
    "Empty Box Delivery":   "WEIGHT_ANOMALY",
    "Counterfeit Product":  "IDENTITY_CONFLICT",
    "Used Product":         "IDENTITY_CONFLICT",
    "Wrong Product":        "IDENTITY_CONFLICT",
    "Pickup Failure":       "TEMPORAL_CONFLICT",
    "Refund Delayed":       "TEMPORAL_CONFLICT",
    "Damaged Product":      "WEIGHT_ANOMALY",
    "Missing Item":         "WEIGHT_ANOMALY",
}

# Lines 124-148: Inject exact matching physical anomalies
if ctype == "WEIGHT_ANOMALY":
    returned_weight = int(original_weight * 0.25)  # 75% drop injected
    evidence += [
        {"source": "WAREHOUSE", "sku": sku, "weight": original_weight, "timestamp": "..."},
        {"source": "CARRIER",   "weight": original_weight,              "timestamp": "..."},
        {"source": "RETURN",    "sku": sku, "weight": returned_weight,  "timestamp": "..."},
    ]
elif ctype == "IDENTITY_CONFLICT":
    wrong_sku = sku[:-1] + chr(ord(sku[-1]) + 1)   # SKU mutation injected
    evidence += [
        {"source": "WAREHOUSE", "sku": wrong_sku, "weight": original_weight, "timestamp": "..."},
        {"source": "RETURN",    "sku": wrong_sku, "weight": original_weight, "timestamp": "..."},
    ]
elif ctype == "TEMPORAL_CONFLICT":
    # Timestamp inversion injected: Carrier scan before Warehouse dispatch!
    evidence += [
        {"source": "WAREHOUSE", "sku": sku, "weight": original_weight, "timestamp": "2026-01-16T08:00:00Z"},
        {"source": "CARRIER",   "weight": original_weight,              "timestamp": "2026-01-15T06:00:00Z"},
    ]
```

### 3.2 Target Leakage Analysis
The reconciliation engine in [`ReconciliationEngine`](TriNetra%20AI/phase-1/engine/reconciliation_engine.py) checks:
1. `if abs(return_weight - original_weight) / original_weight > 0.15` -> flags `WEIGHT_ANOMALY`.
2. `if outbound_sku != return_sku` -> flags `IDENTITY_CONFLICT`.
3. `if carrier_timestamp < warehouse_timestamp` -> flags `TEMPORAL_CONFLICT`.

Because `build_real_dataset.py` injected 75% weight drops, explicit SKU mutations, and 48-hour timestamp inversions, the detection rule was guaranteed to trigger on 100% of positive cases. 

This is **pure target leakage / label circularity**: the evaluation did not test whether TriNetra can detect disputes from ambiguous evidence; it tested whether `ReconciliationEngine` can detect the exact hardcoded synthetic anomalies placed there seconds earlier by `build_real_dataset.py`.

---

## 4. Finding 3: Target Leakage and Invariant Baselines

### 4.1 Rigged Single-Dimension Baselines
- **Affected File:** [`TriNetra_Mobile/TriNetra AI/phase-1/evaluate_real_complaints.py`](TriNetra%20AI/phase-1/evaluate_real_complaints.py)
- **Output File:** [`TriNetra_Mobile/TriNetra AI/results/real_complaint_results.json`](TriNetra%20AI/results/real_complaint_results.json)

In `evaluate_real_complaints.py`, TriNetra is compared against three baselines:
- Baseline 1 (`Baseline1IdentityOnly`): Only checks SKU string equality. Blind to weight drops and timeline inversions.
- Baseline 2 (`Baseline2WeightOnly`): Only checks weight delta. Blind to SKU swaps and timeline inversions.
- Baseline 3 (`Baseline3TimelineOnly`): Only checks timestamp monotonicity. Blind to weight drops and SKU swaps.

Because the evaluation corpus (271 cases) was partitioned into ~91 identity conflicts, ~46 weight anomalies, and ~23 temporal conflicts:
- Baseline 1 was mathematically doomed to miss 69 cases (46 weight + 23 temporal), achieving a False Negative Rate (FNR) of **43.1%**.
- Baseline 2 missed 114 cases (91 identity + 23 temporal), achieving an FNR of **71.3%**.
- Baseline 3 missed 137 cases (91 identity + 46 weight), achieving an FNR of **85.6%**.
- TriNetra simply combined all three checks (`b1 or b2 or b3`), achieving an artificial **0.0% FNR (100% recall, 100% precision, F1=1.000)**.

### 4.2 Spurious Statistical Claims
In `real_complaint_results.json`:
- Reported McNemar chi-squared: `67.0145`
- Reported p-value: `2.695e-16`
- Claimed: *"STATUS: PASSED — Real-world FN reduction > 15% (p < 0.05)"*

This statistical significance is scientifically meaningless. A composite rule checking three conditions will always trivially achieve lower false negatives than three dummy models that each check only one condition, especially when the test dataset is synthetically constructed to contain an even mix of all three conditions.

---

## 5. Finding 4: Injected Risk Score Correlation

### 5.1 Hardcoded Demographic & Dispute Variables
- **Affected File:** [`TriNetra_Mobile/TriNetra AI/phase-2/validation/validate_against_real_data.py`](TriNetra%20AI/phase-2/validation/validate_against_real_data.py)

In Phase 2, the team developed `RiskScoringService`, which calculates a 5-factor fraud risk score based on order price, buyer return rate, seller dispute rate, and evidence completeness.

When testing `RiskScoringService` against `customer_complaints_dataset.csv`, lines 48–66 fabricated customer transaction histories out of thin air based purely on the `Severity` string:
```python
# validate_against_real_data.py: lines 48-66
if sev == "CRITICAL":
    buyer_ret = 25 if "SCAM" in ctype.upper() or "EMPTY" in ctype.upper() else 18
    seller_disp = 45
    price = 9500.0
    ev_sources = 4
elif sev == "HIGH":
    buyer_ret = 12
    seller_disp = 22
    price = 3200.0
    ev_sources = 4
else: # Medium / Low
    buyer_ret = 2
    seller_disp = 4
    price = 650.0
    ev_sources = 5
```

### 5.2 Fabricated Correlation Claims
Lines 142–158 perform a correlation check:
```python
# Check 4: Higher severity correlates with higher fraud risk
corr = results_df["severity_numeric"].corr(results_df["risk_score"])
print(f"  Pearson correlation: {corr:.4f}")
assert corr > 0.60
```
The report asserts this proves that *"higher complaint severity correlates with higher fraud risk in real-world data"*. In reality, the correlation was directly forced by the `if/elif/else` block that assigned higher prices, higher buyer return rates, and higher seller dispute histories to complaints tagged "CRITICAL".

---

## 6. Finding 5: Simulated Backend Verification & Latency Forgery

### 6.1 Fabricated Online Latencies When Service Was Dead
- **Affected File:** [`TriNetra_Mobile/testing/real_world_validation.py`](testing/real_world_validation.py)
- **Target File:** [`TriNetra_Mobile/testing/validation_output/real_world_validation_report.md`](testing/validation_output/real_world_validation_report.md)

In `real_world_validation.py`, 20 complaints were selected to test the live Spring Boot backend endpoint (`http://localhost:8080/api/claims/verdict`).

Lines 448–475 handle connection failures:
```python
except urllib.error.URLError as e:
    backend_errors += 1
...
# If all backend calls failed, show realistic simulated numbers
if backend_errors == len(selected_20):
    backend_status       = "BACKEND_OFFLINE - Results are SIMULATED"
    p50, p95, p99, avg   = 142, 267, 398, 178
    backend_correct      = 18
    backend_success_rate = "18/20 (Simulated - backend offline during validation run)"
    backend_pct          = 90
    for r in backend_results:
        r["verdict"]  = "SIMULATED"
        r["correct"]  = True
```

When the validation script was executed without the backend running, rather than failing the build or exiting with an error, the script forged execution metrics:
- It reported P50 latency of **142 ms**, P95 of **267 ms**, P99 of **398 ms**, and average of **178 ms**.
- It reported accuracy of **18/20 (90%)**.
- In `real_world_validation_report.md`, line 93 printed: `SLA: PASS (all <500ms)`, line 96 printed `OK Zero crashes on real messy data`, and line 97 printed `OK Graceful handling of missing evidence fields`.

Simulating execution times and accuracy scores in an audit report when the backend was offline constitutes falsification of benchmarking outputs.

---

## 7. Finding 6: Cross-Contamination into Current V3 Logistics Verification

### 7.1 Injection of Fake Complaints into Authoritative Logistics Database
- **Affected File:** [`TriNetra_Mobile/backend/src/main/resources/schema.sql`](backend/src/main/resources/schema.sql) (lines 298–326)
- **Reference Doc:** [`TriNetra_Mobile/REAL_DATA_DEMO.md`](REAL_DATA_DEMO.md)

The current V3 architecture (documented in `DECISION_ENGINE.md` and `UNIT_LIFECYCLE.md`) is designed for **pre-delivery physical verification**: serial numbers, IMEI checks, unbroken custody chains, and package seal inspection at sorting hubs.

However, git diff shows that a commit attempted to create a "Real-Data Demo" by inserting three complaint records from the synthetic `trinetra_real_complaints_expanded.csv` into the V3 database:
```sql
-- backend/src/main/resources/schema.sql lines 298-301
INSERT INTO serialized_units VALUES
    ('XS-CMP-00001', 'ORD-20001', 'Footwear', 'SN-AJIO-001', 'IMEI-AJIO-001', 'CMP_00001', 'Ajio', 'Pickup Failure', 'Ordered Adidas sneakers on Ajio. Delivered wrong shoe size...'),
    ('XS-CMP-00002', 'ORD-20002', 'Electronics', 'SN-AMZN-002', 'IMEI-AMZN-002', 'CMP_00002', 'Amazon', 'Counterfeit Product', 'Delivered counterfeit smartwatch...'),
    ('XS-CMP-00003', 'ORD-20003', 'Apparel & Home', 'SN-MSHO-003', 'IMEI-MSHO-003', 'CMP_00003', 'Meesho', 'Used Product', 'Delivered visibly used and damaged item...');
```

`REAL_DATA_DEMO.md` explicitly admits:
> *"The live demo uses three records from TriNetra AI/xscrapper/trinetra_real_complaints_expanded.csv. The complaint records provide source context; the serialized identities are controlled demo identities because the complaint dataset does not contain physical serial/IMEI values."*

### 7.2 Why This Is Severe
1. `CMP_00001`, `CMP_00002`, and `CMP_00003` are not real consumer complaints; they were generated in Python from template variations in `expand_master_dataset.py`.
2. The serial numbers (`SN-AJIO-001`, `SN-WRONG-999`, etc.) were completely invented.
3. This creates the illusion in the React web dashboard and Android app that TriNetra is resolving real consumer grievances through physical scanning, when in fact it is executing pre-programmed checks against synthetic data.

---

## 8. Summary Table of Audit Findings

| Finding ID | Primary File(s) Cited | Line Numbers | Violation Category | Severity |
|---|---|---|---|---|
| **F-01** | `expand_master_dataset.py` | 39–174 | Fabrication of 271 complaint records & placeholder URLs | **CRITICAL** |
| **F-02** | `build_trinetra_1000_corpus.py` | 51–180, 274–348 | Fabrication of 779 additional complaints & /dispute_ URLs | **CRITICAL** |
| **F-03** | `trinetra_complaint_quality_report.md` | 453, 509 | Falsely certifying 0% synthetic data & zero hallucinated facts | **CRITICAL** |
| **F-04** | `build_real_dataset.py` | 36–48, 124–148 | Target leakage / circular physical evidence injection | **CRITICAL** |
| **F-05** | `evaluate_real_complaints.py` | 42–110 | Asymmetric baseline rigging & circular 100% F1 score claims | **HIGH** |
| **F-06** | `validate_against_real_data.py` | 48–66, 142–158 | Injected correlation between severity and fraud risk | **HIGH** |
| **F-07** | `testing/real_world_validation.py` | 448–475 | Forgery of backend latency and accuracy during outage | **HIGH** |
| **F-08** | `backend/src/main/resources/schema.sql` | 298–326 | Database contamination seeding fake complaints into V3 | **HIGH** |
| **F-09** | `trinetra_complaint_sources.csv` | 1–15 | Undocumented licensing; unilateral assertion of fair use | **MEDIUM** |
| **F-10** | `RS_Session_266_AU_2442_A.ii_.csv` | 1–13 | Macro aggregate data misused to validate granular synthetic data | **MEDIUM** |

---

## 9. Conclusion

The audit conclusively proves that the legacy complaint-mining and research pipelines were built on **fabricated inputs, circular evidence, and rigged evaluations**. 

None of the legacy "real complaint" datasets should be used as evidence of real-world validity. The current V3 logistics verification system (Android client and Spring Boot backend) is technically sound in its deterministic architecture, but must be completely purged of legacy complaint dependencies, mock seeds, and misleading validation claims before proceeding.
