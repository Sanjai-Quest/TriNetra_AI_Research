# TriNetra-Link: Status, Pending Work & Next Steps

> **Branch:** `research/trinetra-link`  
> **Last push:** `5e3373b` — 2026-11-01  
> **Watermark:** ALL synthetic outputs carry `SYNTHETIC DRY RUN — NOT A RESULT`

---

## ✅ What Is DONE (committed & pushed)

| Commit | What it delivered |
|--------|-------------------|
| `a52c019` | **Phase A** — core method package (`attribution/`, `reconcile/`, `quality/`, `schema/`) |
| `26dea53` | **Phase B** — ingest + capture path (`ingest/api.py`, SQLite store) |
| `1331fab` | **Phase C** — staging tools: assignment, split, audit, pilot, scale characterisation, ground-truth commit |
| `690f68c` | **Phase D** — baselines (B1–B5) + experiments E1, E2, E3 |
| `51967b5` | **Phase E** — Streamlit investigator viewer, reproducibility docs |
| `b535550` | **Demo** — `trinetra demo generate`, `trinetra demo run`, refusal guards, viewer mode |
| `2d67121` | **Audit fixes** — gates G-3/G-4 set PENDING, tare reconciliation, label protocol fix |
| `e50109d` | **Six integrity fixes** — glare → low q_photo, seal-from-dark-photo blocked, ABSTAIN_DEGRADED logic, theta clamped [0.3, 0.9] |
| `ea74747` | **Step 1** — B1 redefined as CP4-only current practice, B2 as endpoints, `--mask full\|field` evaluator, subgroup tables |
| **`5e3373b`** ← *current HEAD* | **Step 2 partial** — `SealObservation` schema, `breach_depth` on `Attribution`, `.gitignore` (pilot_kit/, main_kit/), `scripts/make_staging_kit.py`, `docs/TRINETRA_IN_DATASET.md` |

---

## ⏳ Step 2 (Layered Seals) — PARTIALLY DONE, PENDING items

Step 2 was started but the server restarted before the remaining instructions were completed. The schema is in place; the logic, generator update, viewer, and eval pieces are still missing.

### What's still needed (in order):

---

### 2-A: `trinetra_link/reconcile/seals.py` ← **NOT CREATED YET**

Create this file with:

```python
# reconcile_seal_layers(checkpoints, target_cp_index) -> Dict[str, str]
# Returns {layer_name: "INTACT" | "ANOM" | "UNK"} for each of L1_FWD, L1_RET, L2_BOX, L3_ITEM
#
# Rules:
#   - L1_FWD: check seal_id_read at CP2 against l1_fwd_seal recorded at CP1
#             UNLESS carrier_log at CP2 contains "flyer replaced ... new seal <ID>"
#             and the new ID matches — then NOT anomalous.
#   - L2_BOX, L3_ITEM: check at every checkpoint CP2–CP4 against CP1 recorded IDs.
#   - L1_RET: check at CP4 against l1_ret_seal recorded at CP3.
#   - TORN or MISSING state → ANOM
#   - seal_id_read differs from reference ID → ANOM
#   - UNREADABLE → UNK (never INTACT)
#
# determine_breach_depth(checkpoints) -> str
# Returns one of: "none", "L1_only", "box_entered", "full_substitution"
```

Export in `trinetra_link/reconcile/__init__.py`.

---

### 2-B: `trinetra_link/staging/assign.py` — reuse `make_staging_kit.py` ← **NOT DONE**

The existing `assign_staging_cells()` generates its own simple journey codes. It must be **refactored** to call `scripts.make_staging_kit.build_assignment(MAIN_CELLS, seed)` and `split_calibration()` for the actual staging study, so the physical kit and the internal assignment share the same RNG/seed logic.

> **Note:** The existing tests (`test_staging_assignment_quotas_and_reproducibility`, etc.) rely on the current `JRN-2026-XXXX` format. Only change the physical-kit path, not the synthetic generator path used by tests.

---

### 2-C: `trinetra_link/eval/pipeline.py` — integrate seal layers ← **NOT DONE**

In `predict_trinetra_link()`:
1. Add `disable_seals: bool = False` parameter.
2. After the identity reconcile step (line ~143), call `reconcile_seal_layers(cps, k)` for each checkpoint.
3. Integrate per-layer seal anomalies as additional `modality_evidence` entries (e.g. `"seal_L2"`, `"seal_L3"`).
4. After attribution, set `attr.breach_depth = determine_breach_depth(journey.checkpoints)`.

In `trinetra_link/attribution/bayes.py`:
- Handle the new layered seal modality names in `attribute_bayes()` (they work through `modality_evidence` so may just work once the key names are consistent).

---

### 2-D: `trinetra_link/demo/make_synthetic_dryrun.py` — layered seals in generator ← **NOT DONE**

Update `generate_synthetic_dryrun_dataset()` to:
1. Populate `cp.seals` as `List[SealObservation]` for L1_FWD, L2_BOX, L3_ITEM (applied at CP1), and L1_RET (applied at CP3).
2. Use the `seal_action` field from `make_staging_kit.build_assignment()` to set correct states: `"torn"` → TORN, `"replaced"` → different `seal_id_read`, `"subtle"` → UNREADABLE on one layer.
3. Weights are **BOX-ONLY** (no flyer tare, `tare_delta_g = 0.0` for flyer changes affecting only flyer mass).
4. Add `seal_action`, `weight_matched`, `mass_change_g` columns to `staging_log_120.csv`.

---

### 2-E: `trinetra_link/viewer/` — show seal layers in UI ← **NOT DONE**

In the Streamlit viewer (`viewer/app.py`) and/or the static frontend:
1. Pass `cp.seals` in the API checkpoint payload.
2. Render L1/L2/L3 seal state badges per checkpoint in the timeline card.
3. Show `breach_depth` on the verdict card (e.g. "Box entered (L2/L3 breached)").

---

### 2-F: `trinetra_link/eval/e3.py` — "No Seals" ablation ← **NOT DONE**

Add `"Ablation: No Seals"` entry in `ablation_configs`:
```python
"Ablation: No Seals": lambda j: predict_trinetra_link(j, mode="algorithm1", disable_seals=True),
```

---

### 2-G: `trinetra_link/eval/e1.py` — subgroup by `seal_action` ← **NOT DONE**

Once `staging_log_120.csv` has `seal_action` and `weight_matched` columns, extend subgroup eval to report metrics broken down by `seal_action` (torn / replaced / subtle / all_decoy) and `weight_matched` (yes / no / n/a).

---

### 2-H: Tests for seal reconciliation ← **NOT DONE**

Create `tests/test_reconcile_seals.py` with at least:
- A fixture where L2 is TORN → `determine_breach_depth` returns `"box_entered"`.
- A fixture where all IDs changed → returns `"full_substitution"`.
- A fixture where flyer replaced with logged note → L1_FWD is NOT anomalous.
- A fixture where photo is dark (UNREADABLE) → returns UNK, not ANOM.

---

## 🛑 B1 Misattribution Count (blocked until 2-D is done)

Per the Step 2 spec: report how many tampered journeys (ground-truth stage ≠ S2) are wrongly attributed to the customer by B1 (CP4-only baseline). This requires the subgroup columns `seal_action` and `weight_matched` in `staging_log_120.csv`, which depends on 2-D.

---

## 🔮 Step 3 (Future — NOT started)

The following are **not started** and should be tackled after Step 2 is complete:

- **Conformal prediction sets** (three-eye framework): produce set-valued predictions so that the true label is always in the set with calibrated coverage ≥ 90%.
- **Selective conformal abstention**: abstain when the conformal set is `{all stages}` (fully uncertain).
- **Experiments E4–E5**: efficiency of conformal sets vs. posterior-based abstention.
- **Real dataset integration**: swap the synthetic 120-journey generator for actual physical observations once the staging study runs.
- **Mobile app** (`android/`): the APK at `android/app/build/outputs/apk/debug/app-debug.apk` is built but not wired to the live ingest API (`ingest/api.py`).
- **Gate G-3 and G-4**: currently set to `PENDING` in the audit — these pre-registration gates require the physical study to be complete before they can be signed off.

---

## 🧪 Running tests locally

```bash
cd TriNetra_Mobile
python -m pytest tests/ -q
```

All **100 tests** should pass on `HEAD = 5e3373b`. If you see failures in `test_reconcile_seals.py`, it is because `reconcile/seals.py` hasn't been created yet (Step 2-A above).

---

## 📂 Key file map

```
trinetra_link/
  schema/models.py          ← SealObservation, breach_depth on Attribution (DONE)
  schema/__init__.py        ← exports SealObservation (DONE)
  reconcile/
    seals.py                ← MISSING — create for Step 2-A
    fuse.py                 ← integrate seal layers (Step 2-C)
    identity.py, visual.py, weight.py
  staging/assign.py         ← reuse make_staging_kit (Step 2-B)
  demo/make_synthetic_dryrun.py  ← add layered seals (Step 2-D)
  eval/
    pipeline.py             ← integrate seals + breach_depth (Step 2-C)
    e1.py                   ← subgroup by seal_action (Step 2-G)
    e3.py                   ← No-Seals ablation (Step 2-F)
  viewer/app.py             ← seal layer UI (Step 2-E)
  attribution/bayes.py      ← already handles modality_evidence (likely OK)
scripts/make_staging_kit.py ← physical staging kit generator (DONE — do not modify)
docs/TRINETRA_IN_DATASET.md ← dataset description (DONE — do not modify)
tests/
  test_reconcile_seals.py   ← MISSING — create for Step 2-H
```

---

## ⚡ Quick resume command

When you're ready to continue Step 2, paste this into a new session:

```
Continue Step 2 (layered seals) from instruction 2-A.
seals.py is missing — create reconcile/seals.py with reconcile_seal_layers() and 
determine_breach_depth(), then proceed through 2-B to 2-H in order.
Do NOT modify scripts/make_staging_kit.py or docs/TRINETRA_IN_DATASET.md.
Run pytest tests/ -q after each sub-step. Push when all pass.
```
