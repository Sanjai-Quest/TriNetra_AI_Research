# TriNetra AI — Phase 1: Research MVP & Evidence Reconciliation Engine

[![Python 3.12](https://img.shields.io/badge/Python-3.12-yellow.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Statistical Significance](https://img.shields.io/badge/McNemar%20p--value-3.30e--13-success.svg)](https://en.wikipedia.org/wiki/McNemar%27s_test)
[![False Negative Reduction](https://img.shields.io/badge/FN%20Reduction-100%25-brightgreen.svg)](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/results/PHASE_1_RESULTS.md)

Phase 1 implements and experimentally validates the core scientific research hypothesis of TriNetra AI:
> *"Can cross-organizational, multi-source evidence reconciliation reduce false negatives compared with single-source verification?"*

Execution is 100% deterministic, seed-locked (`seed=42`), mathematically formulated, and grounded in relational schemas and Python statistical logic without unverified LLM hallucinations.

---

## 📑 Research Paper Cross-References & Tags

For drafting the research paper, the Phase 1 methodology, formal mathematics, and empirical benchmarks are tagged and indexed in:
* **Master Research Document:** [`TRINETRA_AI_MASTER_RESEARCH_DOCUMENTATION.md`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/TRINETRA_AI_MASTER_RESEARCH_DOCUMENTATION.md) (Sections 9, 10, 13, 14, 15, 20, 21, 22, 23)
* **Authoritative Results Report:** [`phase-1/results/PHASE_1_RESULTS.md`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/results/PHASE_1_RESULTS.md)
* **Mathematical Evidence Model:** [`phase-1/specs/evidence_model.md`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/specs/evidence_model.md)
* **Deterministic Conflict Taxonomy:** [`phase-1/specs/conflict_taxonomy.md`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/specs/conflict_taxonomy.md)
* **1,000-Case Synthetic Dataset:** [`phase-1/data/synthetic_evidence.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/data/synthetic_evidence.csv)
* **Ground Truth Classifications:** [`phase-1/data/ground_truth.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/data/ground_truth.csv)
* **Experimental Results Matrix:** [`research/experiments/results_registry.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/research/experiments/results_registry.csv)

---

## 🔬 Scientific & Algorithmic Modules

1. **Canonical Normalizer ([`normalization/canonical_normalizer.py`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/normalization/canonical_normalizer.py)):** Standardizes heterogeneous units (grams, kg, lbs, oz $\rightarrow$ grams), dimensions, ISO 8601 UTC timestamps, and SKU strings.
2. **Entity Resolution Engine ([`resolution/entity_resolver.py`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/resolution/entity_resolver.py)):** Maps vendor-specific barcodes, ASINs, and serial numbers to canonical product UUIDs.
3. **Deterministic Reconciliation Engine ([`engine/reconciliation_engine.py`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/engine/reconciliation_engine.py)):** Executes formal conflict rules (Identity Mismatch, SKU Conflict, Weight Anomaly, Temporal Inversion, Missing Chain-of-Custody).
4. **Comparator Baselines Suite ([`baselines/`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/baselines/)):**
   - **Baseline 1 (Identity Only):** Standard barcode/SKU matching.
   - **Baseline 2 (Weight Only):** Single-scale departure/return delta.
   - **Baseline 3 (Timeline Only):** Chronological return policy cutoff.
5. **Statistical Evaluation & McNemar Test ([`evaluation/evaluator.py`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-1/evaluation/evaluator.py)):** Computes Precision, Recall, F1, FNRR, Confusion Matrices, and 2x2 contingency Chi-Square significance.

---

## 📊 Empirical Validation Results ($N = 1,000$ cases)

| Metric | Baseline 1 (Identity Only) | Baseline 2 (Weight Only) | Baseline 3 (Timeline Only) | **TriNetra AI (Multi-Source)** | Target Threshold |
|---|---|---|---|---|---|
| **True Positives (TP)** | 30 | 40 | 15 | **95** | — |
| **False Positives (FP)** | 0 | 0 | 0 | **0** | — |
| **True Negatives (TN)** | 905 | 905 | 905 | **905** | — |
| **False Negatives (FN)** | 65 | 55 | 80 | **0** | — |
| **Precision** | 1.0000 | 1.0000 | 1.0000 | **1.0000** | $\ge 0.80$ ✅ |
| **Recall** | 0.3158 | 0.4211 | 0.1579 | **1.0000** | $\ge 0.75$ ✅ |
| **F1 Score** | 0.4800 | 0.5926 | 0.2727 | **1.0000** | $\ge 0.77$ ✅ |
| **FN Reduction vs Best Baseline** | 0.0% | 0.0% | 0.0% | **100.0%** | $> 15.0\%$ ✅ |

* **McNemar's Test vs. Best Baseline (Weight-Only):** $\chi^2 = 53.02, p = 3.3048 \times 10^{-13}$ ($p < 0.0001 \ll 0.05$).

---

## ⚡ Reproducibility Instructions

### 1. Run Pipeline Unit Tests
```bash
python -m unittest discover -s phase-1/tests -p "*.py"
```

### 2. Execute Full Experiment Pipeline
```bash
python phase-1/generate_and_evaluate.py
```
*(Regenerates all predictions, confusion matrices, ablation tables, and metrics in `phase-1/results/`)*.
