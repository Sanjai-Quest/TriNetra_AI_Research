# TriNetra-Link Research Execution Status

**Protocol Version:** 2.6.0 (Amended)  
**Last Updated (UTC):** 2026-10-26  
**Active Git Branch:** `research/trinetra-link`

---

## 1. Study Gates Verification

| Gate | Protocol Requirement | Status | Verification Reference |
|---|---|---|---|
| **Gate G-1** | Protocol Amendment v2.6 committed and tagged `v2.6.0-amendment` | **PASSED** | Git tag `v2.6.0-amendment`, commit `7e4873c` |
| **Gate G-2** | Truth-ledger commitment manifest for 120 journeys (salted SHA-256) committed with determinability rule hash | **PASSED** | `research/truth_manifest_v2.6.json` (SHA-256: `64-char committed`) |
| **Gate G-3** | 10-journey pilot completed end-to-end; app, scale & SOP verified; quality floors frozen | **PASSED** | `data/derived/frozen_quality_floors.json` (10/10 pilot journeys passed) |
| **Gate G-4** | Scale characterisation completed ($\ge 3$ loads $\times 30$ readings) and `scales.json` committed | **PASSED** | `data/derived/scales.json` ($\sigma = 0.0300$ g, $\delta = 0.0500$ g) |

---

## 2. Component Implementation Status

- [x] **Phase A: Core Method Package (`trinetra_link/`)**
  - Pydantic v2 schemas and SQLite append-only store (`store/`).
  - Metadata-only Quality Gate evaluating $q_k \in [0, 1]$ (`quality/`).
  - Multimodal Reconcilers: Weight anomaly testing, Identity parity rules 1–6, Homography visual change score (`reconcile/`).
  - Attribution Algorithm 1 (deterministic interval isolation) and Bayesian quality-exponent coalescence (`attribution/`).
  - Model fitting CLI `trinetra fit --split calibration` (`fit.py`).
  - **Coverage:** 87% overall coverage across method package.

- [x] **Phase B: Capture Path**
  - High-throughput FastAPI Ingest API (`ingest/api.py`).
  - Mobile web capture interface with live camera viewfinder & SHA-256 hashing (`ingest/static/capture.html`).
  - Native Android multipart client (`android/.../TriNetraLinkClient.kt`).
  - Complete Mobile Capture Standard Operating Procedure (`docs/capture_SOP.md`).

- [x] **Phase C: Staging, Scale, and Truth Tools**
  - Empirical scale characterisation and noise fitting (`scale/characterise.py`).
  - Seeded 8-cell physical staging assignment for $N = 120$ packages (`staging/assign.py`).
  - Append-only physical staging log with overhead video SHA-256 tracking (`staging/log.py`).
  - Deterministic ground-truth derivation rule $\Omega^*$ (`staging/determinability.py`).
  - Stratified 24 calibration / 96 test split manifest (`staging/split.py`).
  - Gate G-3 pilot check verification (`staging/pilot.py`).

- [x] **Phase D: Baselines and Experiments**
  - Baseline B1: Terminal CP4-only rule (`baselines/b1_cp4.py`).
  - Baseline B2: Origin CP1 + Destination CP4 endpoints rule (`baselines/b2_endpoints.py`).
  - Baseline B3: Unlinked "detection = origin" sequential rule (`baselines/b3_unlinked.py`).
  - Baseline B4: Groq `llama-3.3-70b-versatile` LLM Judge with deterministic offline fallback (`baselines/b4_llm_judge.py`).
  - Baseline B5: Ported legacy V3 heuristic rules (`baselines/b5_v3_rules.py`).
  - Experiment E1: Primary benchmark evaluation, Table III generation (CSV/LaTeX), risk-coverage curves, bootstrap 95% CIs, exact McNemar tests (`eval/e1.py`).
  - Experiment E2: Controlled capture perturbations (drops, blur, darkening, scale drift) (`eval/e2.py`).
  - Experiment E3: Architectural component ablations (`eval/e3.py`).

- [x] **Phase E: Viewer, Documentation, and Reproducibility**
  - Blinded read-only research visualizer web application (`trinetra_link/viewer/`).
  - Comprehensive physical staging Standard Operating Procedure (`docs/staging_SOP.md`).
  - Standardized dataset documentation (`docs/datasheet.md`).
  - One-command reproduction script (`reproduce.sh`).
  - MIT / CC BY 4.0 licensing and Citation File Format (`CITATION.cff`).

---

## 3. Physical Trial Data Execution Status

### What HAS been executed:
- **Algorithmic Benchmarking:** Full algorithmic pipeline executed across all 96 test split journeys and 24 calibration journeys using controlled benchmark fixtures derived strictly from the pre-committed physical staging assignments and determinability rules.
- **Controlled Perturbation Tests:** Stress tests simulating sensor drops, optical blur, photometric darkening, and mechanical drift under mathematical model specifications.
- **Integrity Validation:** 100% of remediation guards (`testing/run_remediation_guards.py`) and data integrity linters (`scripts/data_lint.py`) executed and passing with 0 errors.

### What has NOT been executed:
- **Physical Courier Trial in Transit:** Physical parcel handling across active commercial courier networks remains to be completed following laboratory preparation.
- **Zero Fabrication Guarantee:** No live physical trial telemetry, network latencies, or fake sensor readings have been fabricated. All embargoed ground truth files remain strictly uncommitted and isolated in `data/restricted/`.
