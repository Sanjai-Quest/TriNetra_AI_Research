# Research Reproducibility Audit: Evaluation Metrics, Dependencies, and Validation Claims

**Audit Authority:** Senior Data Engineering & Research Reproducibility Engineer  
**Audit Scope:** TriNetra AI & TriNetra Mobile Codebase  
**Date of Audit:** October 2026  
**Status:** COMPLETE (Read-Only Phase 0 Investigation)

---

## 1. Executive Summary

A core standard of scientific and engineering rigor is reproducibility: can an independent auditor take the raw data, execute the documented transformation code, run the evaluation algorithms, and achieve the reported performance metrics?

This audit evaluated all reported metrics across six distinct evaluation suites in the TriNetra codebase. The findings reveal a stark divergence between **computational reproducibility** and **scientific validity**:

1. **Computational Reproducibility:** Several reported numerical tables (e.g., Phase 1 `real_complaint_results.json`, confusion matrices, and the 15 synthetic test results) can be reproduced down to the decimal point from the saved prediction CSVs.
2. **Scientific Validity:** The evaluation results are **fundamentally non-reproducible in the real world** because the underlying input data consists of template-generated synthetic complaints, circular telemetry injection, rigged single-dimension baselines, and hardcoded simulation fallbacks.

Below is the exhaustive audit of each result suite, identifying exact code dependencies, execution obstacles, and statistical fallacies.

---

## 2. Reproducibility Status Matrix

| Evaluation Suite | Primary File(s) Cited | Reported Key Metrics | Computational Reproduction | Scientific Real-World Validity | Primary Failure Mode |
|---|---|---|---|---|---|
| **Suite 1: Phase 1 Real Complaint Benchmark** | `evaluate_real_complaints.py`, `real_complaint_results.json` | TriNetra: Precision=1.0, Recall=1.0, F1=1.000; Baseline FNR=43.1%; p=2.7e-16 | **REPRODUCED** (Exact match) | **FAILED** | Circular evidence injection; target leakage; rigged baselines |
| **Suite 2: Phase 1 Synthetic 1,000 Cases** | `generate_and_evaluate.py`, `metrics.csv`, `predictions.csv` | TriNetra F1=0.998; Baselines F1=0.25-0.72; FN reduction >70% | **REPRODUCED** (Exact match) | **FAILED** | Synthetic generator injects isolated defect modes matched to baselines |
| **Suite 3: Phase 2 Risk Scoring Validation** | `validate_against_real_data.py`, `test_claim.ps1` | Zero score bounds errors; severity correlation >0.60; 0 Red Flags | **REPRODUCED** (Assertions pass) | **FAILED** | Transaction histories and prices hardcoded from severity strings |
| **Suite 4: Dispute Gap Analysis ("Dark Data Chasm")** | `real_world_validation.py`, `evidence_gap_analysis.csv` | 100% Weight missing; 100% CCTV missing; 36% Physical evidence missing | **REPRODUCED** (Exact match) | **FAILED** | Tautology: counts text in hardcoded constant column `evidence_missing` |
| **Suite 5: Testing Backend Verification** | `real_world_validation.py`, `real_world_validation_report.md` | Accuracy: 18/20 (90%); P50=142ms, P95=267ms; SLA: PASS | **FAILED / FORGED** | **FAILED** | When backend was offline, script forged latencies & simulated accuracy |
| **Suite 6: End-to-End Synthetic Scenarios** | `real_world_validation.py`, `performance_report.md` | 15/15 Passed (100%); F1=1.000; P50=1.29ms | **REPRODUCED** | **PARTIAL** | Valid unit integration test; misrepresented as "real-world validation" |

---

## 3. Deep-Dive Audit by Evaluation Suite

### 3.1 Suite 1: Phase 1 Real Complaint Evaluation (`real_complaint_results.json`)

#### Recomputed Metrics vs. Saved File:
Using our independent scratch audit script ([`reproduce_phase1.py`](reproduce_phase1.py)), we recomputed the full confusion matrix from [`real_complaint_predictions.csv`](TriNetra%20AI/data/real_complaint_predictions.csv):

```text
Model         | Recomputed (TP, FP, TN, FN) | Saved in JSON           | Exact Match?
------------- | --------------------------- | ----------------------- | ------------
Baseline 1    | TP=91,  FP=0, TN=111, FN=69 | TP=91,  FP=0, TN=111, FN=69 | TRUE
Baseline 2    | TP=46,  FP=0, TN=111, FN=114| TP=46,  FP=0, TN=111, FN=114| TRUE
Baseline 3    | TP=23,  FP=0, TN=111, FN=137| TP=23,  FP=0, TN=111, FN=137| TRUE
TriNetra      | TP=160, FP=0, TN=111, FN=0  | TP=160, FP=0, TN=111, FN=0  | TRUE
```

#### McNemar Statistical Test Recomputation:
- Contingency: $n_{00}=0, n_{01}=69, n_{10}=0, n_{11}=202$
- Continuity-corrected $\chi^2 = \frac{(|69 - 0| - 1)^2}{69 + 0} = \frac{68^2}{69} = \mathbf{67.0145}$
- Saved $\chi^2$: **67.0145** (Exact match)
- Saved $p$-value: **$2.695 \times 10^{-16}$**

#### Why This Scientific Result Is Void:
Although the arithmetic is 100% accurate, the underlying experiment is completely ungrounded:
1. `customer_complaints_dataset.csv` contains 271 template-generated synthetic complaints.
2. `build_real_dataset.py` read those complaints, took the label `WEIGHT_ANOMALY`, and inserted `returned_weight = original_weight * 0.25`.
3. `ReconciliationEngine` checks if weight dropped by $>15\%$.
4. Claiming a $p$-value of $10^{-16}$ for an algorithm detecting a 75% weight drop that its own companion script hardcoded into the input is a violation of experimental validity.

---

### 3.2 Suite 4 & 5: Testing Gap Analysis & Simulated Backend Verification

#### The "Dark Data Chasm" Fallacy:
[`real_world_validation_report.md`](testing/validation_output/real_world_validation_report.md) asserts:
> *"Weight / Scale Records Missing: 1050/1050 (100%)"*  
> *"Warehouse Pack-Station CCTV Missing: 1050/1050 (100%)"*  
> *"Carrier GPS Timestamps Missing: 1050/1050 (100%)"*  
> *"In 36% of real disputes, investigators have ZERO measurable physical evidence."*

#### Forensic Root Cause:
In [`testing/real_world_validation.py`](testing/real_world_validation.py), lines 72–74 calculate this gap by searching for keywords in the column `evidence_missing`:
```python
weight_missing_count = sum(1 for r in records if "weight" in r.get("evidence_missing", "").lower())
cctv_missing_count   = sum(1 for r in records if "cctv" in r.get("evidence_missing", "").lower())
gps_missing_count    = sum(1 for r in records if "checkpoint" in r.get("evidence_missing", "").lower())
```
Our audit script [`audit_tools.py`](audit_tools.py) revealed that **1,050 out of 1,050 rows (100.0%) in `trinetra_real_complaints_expanded.csv` contain the exact identical hardcoded string**:
`"Continuous Unboxing Video; In-transit Checkpoint Weight Log; Pack-station CCTV"`

The 100% "evidence gap" was not discovered by analyzing real carrier databases; it was a constant string assigned in `build_trinetra_1000_corpus.py` (line 330) and then re-read in `real_world_validation.py`.

#### Backend Simulation Forgery:
Lines 465–475 of `real_world_validation.py` state:
```python
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
When an independent researcher runs `real_world_validation.py` without starting the Java backend server on port 8080, the script does not raise an exception. Instead, it generates a report claiming a 90% success rate, sub-500ms SLA compliance, and specific percentiles. This metric is completely fabricated.

---

### 3.3 Suite 6: End-to-End Synthetic Scenarios (`synthetic_disputes.csv`)

#### Analysis:
[`testing/synthetic_disputes.csv`](testing/synthetic_disputes.csv) contains 15 curated scenarios:
- `CLAIM-SYN-001` to `003`: Consistent returns
- `CLAIM-SYN-004` to `007`: Weight anomalies (e.g. iPhone swap with 36% weight drop)
- `CLAIM-SYN-008` to `009`: SKU swaps (e.g. `NIKE-123` returned as `NIKE-FAKE-456`)
- `CLAIM-SYN-010` to `011`: Temporal inversion (return timestamp before delivery timestamp)
- `CLAIM-SYN-012` to `013`: Missing evidence array
- `CLAIM-SYN-014` to `015`: Edge cases (zero outbound weight)

#### Findings:
1. **Valid as a Unit Test:** When the V3 backend is running, sending these 15 payloads returns the expected status for all 15 cases. This is a functional regression test.
2. **Invalid as a Research Result:** In [`testing/performance_report.md`](testing/performance_report.md), this 15-row unit test is presented as a validation benchmark:
   > *"Summary: 15/15 TESTS PASSED... F1-Score: 1.0000 (Perfect accuracy on synthetic data) READY FOR DEMO TUESDAY."*  
   Passing 15 unit tests is not validation of a decision system; treating 15 synthetic cases as an F1 score of 1.0000 misrepresents testing fixtures as empirical research results.

---

## 4. Critique of Official Government NCH Benchmark Comparison

In [`datasets/trinetra_complaint_analysis.md`](datasets/trinetra_complaint_analysis.md) (lines 620–634), the author presents a comparative table between the 1,050 generated complaints and official Indian Parliamentary records:

| Dispute Category | Observed in Real Corpus (n=1,050) | NCH Parliamentary Data (n=397,333) | Claimed Alignment |
|---|---|---|---|
| Delivery of Wrong Product | 44.4% | 13.7% | "Aligned (visual shareability)" |
| Defective / Damaged Product | 34.5% | 13.4% | "Strongly Aligned" |
| Paid Amount Not Refunded | 47.0% | 12.8% | "Strongly Aligned" |
| Non-Delivery / Delay | 23.5% | 17.7% | "Strongly Aligned" |

The report concludes:
> *"Research Conclusion: The real-world complaint corpus mirrors the official Government of India grievance taxonomy with statistical fidelity..."*

### Data Engineering Refutation:
1. **The Numbers Do Not Match:** 44.4% vs 13.7% is a $3.2\times$ discrepancy; 47.0% vs 12.8% is a $3.7\times$ discrepancy. Labeling a $3.7\times$ difference as "Strongly Aligned" is mathematically unfounded.
2. **Category Inflation:** In the 1,050 generated dataset, booleans are not mutually exclusive (a record can have `identity_conflict=True` and `refund_conflict=True` simultaneously). In the NCH parliamentary data ([`RS_Session_266_AU_2442_A.ii_.csv`](TriNetra%20AI/Public_Datasets/RS_Session_266_AU_2442_A.ii_.csv)), categories are mutually exclusive primary grievance classifications that sum to 100%. Comparing non-mutually exclusive keyword flags to a single-label government census is statistically invalid.
3. **Macro Aggregate vs. Micro Instance:** An aggregate table reporting 54,563 complaints in India cannot validate 1,050 generated text strings. Aggregate totals provide zero ground truth regarding individual serial numbers, return events, or package weights.

---

## 5. Code, Dependency, and Environment Deficiencies

During the reproduction audit, several code and environment deficiencies were identified that impair reproducibility:

1. **Hardcoded Windows Absolute Paths in Older Reports:**
   Several validation files in `xscrapper` contain hardcoded paths referencing `c:/Users/mitsu/Downloads/xscrapper/...` (e.g. [`dataset_and_literature_engineering_report.md`](TriNetra%20AI/xscrapper/xscrapper/validation_report/dataset_and_literature_engineering_report.md#L14)).
2. **Missing Live Microservices Infrastructure:**
   Phase 2 services (`claim-service`, `evidence-service`, `fraud-detection-engine`) require PostgreSQL, RabbitMQ, Redis, and MinIO defined in [`docker-compose.yml`](TriNetra%20AI/phase-2/docker-compose.yml). They cannot be executed or tested directly without spinning up Docker containers and migrating databases.
3. **Broken Script Execution from Non-Root CWD:**
   In [`testing/real_world_validation.py`](testing/real_world_validation.py) (line 27), `BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`. If executed from `TriNetra AI/` instead of `TriNetra_Mobile/`, path resolution fails.
4. **Encoding Issues on Standard Windows Consoles:**
   Scripts like `build_trinetra_1000_corpus.py` and `build_real_dataset.py` require `sys.stdout.reconfigure(encoding="utf-8")` because emojis and Unicode characters in generated texts crash default Windows `cp1252` terminal streams.

---

## 6. Summary of Reproducibility Assessment

1. **Can existing results be reproduced mathematically?**  
   **YES.** The mathematical formulas, confusion matrices, and $\chi^2$ calculations reproduce exactly from the saved prediction tables.
2. **Can existing results be reproduced scientifically?**  
   **NO.** The inputs are synthetic fabrications, the ground-truth labels are circular, the baselines are deliberately crippled, and backend metrics were simulated.
3. **Can the current V3 pre-delivery physical verification system be verified?**  
   **YES.** The V3 backend unit test suite ([`V3DecisionEngineTest.java`](backend/src/test/java/com/trinetra/verdict/service/V3DecisionEngineTest.java)) executes deterministically without external database or network dependencies, providing an authentic foundation for physical custody verification.
