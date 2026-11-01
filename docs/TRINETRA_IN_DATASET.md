# TriNetra-IN: The 120-Journey Dataset

> **Where this file goes:** `docs/TRINETRA_IN_DATASET.md` in the repository.
> **Applies to:** Protocol v2.5 as amended by `research/amendments/AMENDMENT_v2.6.md`.
> **Status:** Collection not started. Nothing below describes collected data.

---

## 1. What this dataset is, in one paragraph

TriNetra-IN is a small, real, physically collected dataset of **120 package journeys**. In each journey one parcel passes through four checkpoints of an e-commerce return: seller dispatch, delivery, return pickup and warehouse intake. At every checkpoint we photograph and weigh the parcel. In some journeys a team member deliberately damages, swaps or tampers with the parcel between two checkpoints, and films that action. The video records **where** the change really happened, and that is the ground truth. TriNetra-Link is then asked to work out that stage from the photos and weights alone, or to say honestly that the evidence isn't good enough to tell.

## 2. Why we need it

| Question | Answer |
|---|---|
| Why not use existing data? | No public dataset follows **one parcel across four handovers** with photos and weights. TAMPAR (WACV 2024) compares one pair of images; Indian return studies use surveys or transaction logs. |
| Why not generate it with code or AI? | If a program creates the damage, the same program decides the right answer, so the method just finds what the generator planted and scores perfectly. The project's own `audit/` folder documents this happening in legacy code (F1 = 1.000 from injected anomalies). Generated data is allowed only for demos and unit tests (Section 11). |
| Why 120? | It gives about ±10 percentage-point confidence on accuracy over the 96 test journeys and at least 12 journeys in every scenario type. It is small enough for two people to finish in about 18 hours of hands-on work. |
| Why staged, not real couriers? | A first paper needs ground truth that is known for certain. With real couriers nobody knows where a change truly happened. Staging is disclosed as a limitation. |

## 3. Key terms

| Term | Meaning |
|---|---|
| **Journey** | One parcel going CP1 → CP2 → CP3 → CP4, with evidence captured at each checkpoint |
| **Checkpoint (CP)** | A point where custody changes hands and evidence is recorded |
| **Stage** | The custody interval *between* two checkpoints, where a change can happen |
| **Manipulation** | The physical change the stager performs: damage, swap, removal |
| **Ground truth** | What actually happened and where, taken from the staging log and overhead video |
| **Determinability (Ω\*)** | Whether the captured evidence is good enough to identify the stage: DET (yes), DEG (evidence degraded), IND (evidence ambiguous) |
| **Abstention** | The correct answer when Ω\* is DEG or IND: the method says "cannot tell" instead of guessing |

### The checkpoints and stages

```
CP1 Seller dispatch ──[S1 forward transit]──► CP2 Delivery / OBD ──[S2 customer custody]──►
CP3 Return pickup ──[S3 reverse transit]──► CP4 Warehouse intake
```

| Stage | Between | Output label when the change is found here |
|---|---|---|
| S1 | CP1 → CP2 | `ATTR_STAGE_FORWARD_TRANSIT` |
| S2 | CP2 → CP3 | `ATTR_STAGE_CONSUMER_CUSTODY` |
| S3 | CP3 → CP4 | `ATTR_STAGE_REVERSE_TRANSIT` |
| none | — | `ATTR_CONFIRMED_LEGITIMATE` |

## 4. The 8 scenario types (120 journeys)

| # | Scenario | n | What the stager does | Where | Expected output |
|---|---|---|---|---|---|
| 1 | **Intact** | 30 | Nothing | — | `ATTR_CONFIRMED_LEGITIMATE` |
| 2 | **Permitted flyer-bag change** | 12 | After CP1, move the box into a new flyer closed with a new L1 seal and pass the note "flyer replaced at hub, new seal <ID>". L2 and L3 untouched | — | `ATTR_CONFIRMED_LEGITIMATE` (a logged, allowed change; tests false alarms) |
| 3 | **Forward-transit damage** | 14 | After CP1: drop the parcel about 1 m onto a corner, or dent one face. No seal broken | S1 | `ATTR_STAGE_FORWARD_TRANSIT` |
| 4 | **Doorstep substitution** | 14 | After CP1: swap the whole parcel for a decoy (different item; decoy L1, L2 and L3 seals; mass change 0–150 g) | S1 | `ATTR_STAGE_FORWARD_TRANSIT` (with 4 checkpoints, doorstep and line-haul can't be told apart) |
| 5 | **Customer tamper** | 14 | After CP2: break L2, cut L3, remove 0–150 g (0 g = weight-matched with filler) or swap the item; seals left torn or replaced with look-alikes | S2 | `ATTR_STAGE_CONSUMER_CUSTODY` |
| 6 | **Reverse-transit tamper** | 12 | After CP3: slit the return flyer, break L2/L3, remove 0–150 g; seals left torn or replaced | S3 | `ATTR_STAGE_REVERSE_TRANSIT` |
| 7 | **Degraded evidence** | 12 | One of types 3, 5 or 6, **and** one checkpoint bounding that stage is captured in the dark with the scale recorded as ERROR | S1/S2/S3 | `ATTR_ABSTAIN_DEGRADED` |
| 8 | **Ambiguous evidence** | 12 | One of types 3, 5 or 6 with a **small** defect (cut of 1 cm or less in glossy tape); flash glare covers it at both bounding checkpoints | S1/S2/S3 | `ATTR_ABSTAIN_INDISTINGUISHABLE` |

Mass changes (0, 10, 20, 50, 100 or 150 g; **0 g means weight-matched**: the stager adds filler so the weight does not change, which is how a careful fraudster behaves and which only seal or visual evidence can catch) and the hidden stage in types 7–8 are chosen at random by `make_staging_kit.py`. The planned values are only a plan: **ground truth is what the staging log says actually happened.**

## 4A. Layered tamper-evident seals (who broke it, and how deep)

Every parcel carries three layers of uniquely numbered seals, like jewellery packaging:

| Layer | What it is | Applied | Checked |
|---|---|---|---|
| **L1 transit seal** | QR seal sticker closing the courier flyer, one per leg | Forward seal at CP1, return seal at CP3 | Photographed **before** opening at CP2 (forward) and CP4 (return) |
| **L2 box seal** | QR tamper sticker across the product box opening | At packing, stays the whole journey | Photographed at every checkpoint |
| **L3 item tag** | QR tag tied around the product box with a cable tie | At packing, stays the whole journey | Photographed at every checkpoint |

A seal alone only says *whether* it was broken. TriNetra says *where*: the last checkpoint that photographed seal ID X intact and the first that found it torn, missing or **replaced by a different ID** bound the custody stage in which it happened. The layer says *how deep*: an L1-only change can be a logged, legitimate flyer change; a broken L2 or L3 means the product box was entered.

Tamper journeys use one **seal action**:
- **torn**: broken seals are left visible.
- **replaced**: look-alike seals with different IDs are applied neatly. Only the ID check catches these.
- **subtle**: an L2 corner is lifted and pressed back, used only in ambiguous (glare) journeys.

The kit prints all seal IDs. Genuine, decoy and replacement labels look identical.

## 5. Roles

| Role | Does | Must not |
|---|---|---|
| **Stager (Person A)** | Packs parcels, applies seal labels, performs manipulations on camera, fills the staging log | Capture checkpoints for journeys they staged (when a second person is available) |
| **Capturer (Person B)** | Photographs and weighs at CP1–CP4 following the capture SOP, fills the capture sheet | See the assignment sheet, stager cards or staging log |
| **Analyst** (A, B or a third person) | Runs the code | Change rules, thresholds or labels after seeing test results |

With only one person, follow the single-person procedure in Amendment v2.6 §4.4 and disclose it in the paper.

## 6. Materials

| Item | Quantity | Notes |
|---|---|---|
| Household items | 15–20, reused | Old chargers, cables, phone cases, power banks, soap, books, tins. Value doesn't matter |
| Cable ties | ~180 | To tie the L3 item tags; a cut tie means a broken tag |
| Small cardboard boxes | ~70 | Old delivery boxes. Damaged or slit boxes are retired; intact ones are reused with a **new** seal |
| Poly courier bags | ~150 | |
| Filler masses | 20 / 50 / 100 / 150 g | Washers, coins or sand bags, pre-weighed and labelled |
| Digital kitchen scale | 1 (keep the same one throughout) | 1 g resolution, ≥ 5 kg. No Bluetooth needed |
| Phones | 2 | One on a stand filming manipulations (overhead), one for capture photos |
| Printer, tape, marker, cutter | — | |

## 7. How to create the journeys, step by step

### Step 1: generate the kit (once, 10 minutes)
```bash
pip install reportlab
python scripts/make_staging_kit.py --seed 777 --n 10 --pilot --out pilot_kit
python scripts/make_staging_kit.py --seed <chosen-seed> --n 120 --out main_kit
```
The script creates the random assignment, the 24/96 split, seal labels, stager cards, capture cards, the capture order (8 sessions × 15) and the truth commitment. Section 8 lists every file.

### Step 2: commit the truth commitment (Gate G-2)
Copy `main_kit/public/truth_manifest_main.json` to `research/truth_manifest_v2.6.json`, then commit and push it **before staging anything**. Move `main_kit/restricted/` to `data/restricted/`, which is git-ignored.

### Step 3: measure scale noise (Gate G-4, about 30 minutes per day for 3 days)
Weigh a constant-mass object (for example a sealed water bottle) 30 times at each of 3 loads, lifting it off between readings, and record the results in `data/raw/scale_noise.csv`. Repeat on two more days. This gives each scale's noise σ and drift.

### Step 4: pilot (one evening, 10 journeys, Gate G-3)
Run the pilot kit exactly like the real study. Check that a 20 g change is visible on the scale, that the lighting is realistic and that photos are consistent. Fix the procedure, then **freeze it**. Pilot data is never analysed.

### Step 5: run the 120 journeys (8 sessions of 15, about 2.5 hours each)

For each journey, in `capture_order.csv` order:

1. **Stager** packs an item in a box, adds paper fill, tapes it, sticks on the seal label named on the stager card, and puts it in a courier bag.
2. **Capturer** records **CP1** (capture SOP below).
3. **Stager** takes the parcel out of the capturer's sight. If the card says "after CP1", they perform the manipulation **in front of the overhead camera**; otherwise they just wait about the same time.
4. **Capturer** records **CP2**. Repeat steps 3–4 for "after CP2" → **CP3** and "after CP3" → **CP4**.
5. **Stager** fills the stager card: actual manipulation, mass removed, video file, deviations.

Every parcel leaves the capturer's sight between every pair of checkpoints, including intact ones, so the capturer can't tell which parcels were touched.

**Capture SOP at each checkpoint (about 2–3 minutes):**
1. **Before opening any flyer** (CP2, CP4): photograph the L1 flyer seal close up.
2. Photo of the box **top** from about 40 cm, then the **label side**, same distance.
3. Close-ups of the **L2 box sticker** and the **L3 item tag**, with the QR readable.
4. **Weigh the box only** (never with a flyer), three times, lifting it off between readings.
5. Write the weights, the seal IDs read with their state (intact, torn, missing) and any carrier note.
6. At CP1 and CP3: put the box into a flyer, close it with the seal ID printed on the capture card, and photograph it.
7. Follow any **SPECIAL** line on the capture card (lights off with scale ERROR, or flash glare over the box top).

### Step 6: after each session (10 minutes)
- Copy the photos to `data/raw/<journey_code>/<CP>/` and the videos to `data/restricted/videos/`.
- Type the capture sheet and the staging log.
- Hash each video (`sha256sum`) into the staging log.
- Back up to two places.

## 8. Files and folder layout

```
research/truth_manifest_v2.6.json       PUBLIC  salted SHA-256 commitment per journey (committed before staging)
data/
  raw/                                   capture evidence (released after blurring faces/addresses)
    capture_sheet.csv                    one row per journey x checkpoint
    scale_noise.csv                      repeated weighings for the noise model
    <journey_code>/CP1/{top,label,l1,l2,l3}.jpg
    <journey_code>/CP2/...  CP3/...  CP4/...
  restricted/                            git-ignored; never shown to the capturer or the method
    assignment.csv                       planned cell, stage, mass change, degradation, split
    staging_log.csv                      what ACTUALLY happened (this is the ground truth)
    salts.json                           opens the commitments after the study
    videos/<journey_code>.mp4            overhead video of each staging
  derived/
    scales.json                          fitted σ and drift per scale
```

**`capture_sheet.csv`:**
`journey_code, cp, photo_top, photo_label, photo_l2, photo_l3, photo_l1, w1_g, w2_g, w3_g, scale_id, scale_status, l1_seal_read, l1_state, l2_seal_read, l2_state, l3_tag_read, l3_state, lighting_note, carrier_note, capturer, timestamp_local`

**`staging_log.csv`:**
`journey_code, actual_manipulation, actual_interval, actual_mass_change_g, actual_seal_action, layers_breached, seal_ids_applied_by_stager, degraded_cp_actual, glare_actual, item_id, overhead_video_file, overhead_video_sha256, deviation, notes, stager, start_utc, end_utc`

## 9. How ground truth and determinability are decided (no human raters)

1. **Ground truth stage** = `actual_interval` from the staging log, backed by the overhead video.
2. **Determinability Ω\*** comes from a fixed rule, committed as code before capture (Amendment v2.6 §4.3):

| Staging log says | Ω\* | Correct output |
|---|---|---|
| No manipulation, no degradation | DET | `ATTR_CONFIRMED_LEGITIMATE` |
| Manipulation in stage S, both bounding checkpoints usable | DET | the stage label for S |
| A bounding checkpoint was degraded, or fails the capture-quality check | DEG | `ATTR_ABSTAIN_DEGRADED` |
| Defect hidden by glare at both bounding checkpoints | IND | `ATTR_ABSTAIN_INDISTINGUISHABLE` |

3. **Verification:** after the study, each journey's record plus its salt must reproduce the SHA-256 hash committed before staging. This proves the labels were not edited afterwards.
4. **Optional check:** a second team member re-applies the rule to a random 25% of journeys; report Cohen's κ. No certification is needed.

## 10. How the 120 journeys are used

### 10.1 Split
- **Calibration split: 24 journeys** (20%, stratified by scenario). Used **only** to fit thresholds: the quality-gate cut-off θ, the weight-test multiplier z, the posterior cut-off τ and the visual-change threshold.
- **Test split: 96 journeys.** Used **only** to report results. No threshold or rule may change after looking at it.

### 10.2 What the method sees and what it never sees
| TriNetra-Link sees | TriNetra-Link never sees |
|---|---|
| Photos, weights, scale status, seal QR, timestamps and carrier notes from CP1–CP4 | The assignment sheet, staging log, videos, scenario type or expected label |

### 10.3 Pipeline per journey
1. **Quality gate:** scores each checkpoint's trustworthiness from metadata only (darkness, blur, glare, scale error).
2. **Reconcilers:** compare each checkpoint with CP1. Weight is tested against the scale's measured noise; each seal layer (L1/L2/L3) by ID and state; appearance by photo comparison.
3. **Attribution:** finds the last trusted "intact" and first trusted "changed" checkpoint, then outputs a stage, or abstains if that interval is unclear or contains untrusted evidence.
4. **Score:** compare the output with the ground truth from Section 9.

### 10.4 Experiments
| Experiment | Uses | Reports |
|---|---|---|
| **E1: Method vs. baselines** | 96 test journeys; TriNetra-Link vs. B1 CP4-only, B2 CP1+CP4, B3 "detection = origin", B4 LLM judge (Llama 3.3 via Groq), B5 old V3 serial rules | Stage accuracy (DET journeys), appropriate-abstention rate and unsupported-blame rate (DEG/IND journeys), macro-F1, risk–coverage curve, 95% bootstrap CIs, McNemar tests |
| **E2: Robustness** | The same real test captures, deliberately degraded: a checkpoint removed, blur, darkening, scale drift (5/20/50 g) | How accuracy and abstention change as evidence gets worse |
| **E3: Ablations** | The same test journeys with one component switched off: no quality gate, no visual check, fixed 2 g weight rule | How much each component contributes |

### 10.5 What gets published
- The dataset (photos, weights, logs, ground truth, datasheet), released under CC BY 4.0 with faces and address text blurred.
- Tables III-style results, risk–coverage and robustness figures in the paper, every number traceable to `results/<run_id>/provenance.json`.
- Per-scenario counts with numerators and denominators, including results that don't favour TriNetra-Link.

## 11. Integrity rules

1. **Every journey is physically staged and captured.** No generated, AI-made or edited photos or weights in the dataset.
2. **Synthetic data is allowed only** for unit tests (`tests/fixtures/synthetic/`) and the guide demo (`demo_data/`). It is tagged `"synthetic": true`, stamped "SYNTHETIC DEMO", and never used in results.
3. **Ground truth is the actual event.** Deviations are logged, never "corrected" to match the plan.
4. **The truth commitment is pushed before staging.** The restricted folder is never committed.
5. **Thresholds are fitted on calibration journeys only.** Test results are never used to tune anything.
6. **Failed captures stay in the data** as they happened. A dark photo you didn't intend is still evidence and is scored by the same rule.

## 12. Time and effort

| Task | Time |
|---|---|
| Kit generation + commitment | 15 min |
| Scale noise (3 days) | 30 min/day |
| Pilot (10 journeys) | 1 evening |
| Main study: 8 sessions × 15 journeys | ~2.5 h each, **~18–20 h total** for 2 people |
| After-session upload/typing | 10 min/session |

## 13. FAQ

**Do we need real or new products?** No. 15–20 household items, reused, are enough. The method looks at the package evidence, not at what the product is worth.

**Can we generate the 120 journeys synthetically?** Not for the paper; see Section 2. Synthetic data is fine for the demo and for testing code.

**Do we need certified reviewers?** No. Ground truth comes from the filmed staging log, and determinability from a committed rule (Amendment v2.6).

**What if a manipulation goes wrong, e.g. the seal didn't tear?** Record exactly what happened in the staging log. That becomes the truth for that journey.

**What if we can only do 60?** Halve every scenario type. The paper is still publishable at a conference, with wider confidence intervals (about ±13 pp).

**Can one person do it alone?** Yes, using the single-person procedure (Amendment v2.6 §4.4), disclosed as a limitation.
