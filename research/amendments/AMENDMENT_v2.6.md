# TriNetra Protocol Amendment v2.6.0: Removal of the Human Reviewer Gate

| Field | Value |
|---|---|
| Amends | `research/reviewed_v2/preregistration_protocol_v2.5.md` (tag `v2.5.0-preregistration`, commit `b800e28`) |
| Amendment version | 2.6.0 |
| Date | 2026-10-26 |
| Data collected before this amendment | **None.** No physical journey, capture, rating or model output exists. |
| Effect on blinding | None. The amendment is made before any truth ledger for the new design is created. |

Place this file at `research/amendments/AMENDMENT_v2.6.md`, commit it, and tag the commit `v2.6.0-amendment` **before any package is staged**.

---

## 1. Why the protocol is being amended

Protocol v2.5 made the physical study conditional on Gate E-3: four independent human reviewers had to complete a 10-case calibration pack with Fleiss' κ ≥ 0.60. The project team does not have access to four independent, trained reviewers.

No conference or journal requires "certified" reviewers for this kind of study. Gate E-3 existed only to support one specific design, a human-adjudicator comparison of Condition C (separate records) against Condition D (linked records). That comparison is moved to future work (Section 3), so the gate no longer serves a purpose and is withdrawn.

Ground truth in this study never depended on reviewers. It comes from what was physically done to each package, recorded when it was done (Section 4).

## 2. Summary of changes

| # | v2.5 | v2.6 |
|---|---|---|
| A1 | Primary question: does linked presentation help **human adjudicators**? | Primary question: can an **evidence-quality-aware method** attribute the discrepancy stage and abstain correctly? |
| A2 | Gate E-3: 4 reviewers, Fleiss' κ ≥ 0.60 | **Withdrawn.** Calibration pack and reviewer forms are archived, not deleted |
| A3 | N = 60, scenario cells allocated in sequential ID blocks | N = 120, random assignment and shuffled journey order (Section 5) |
| A4 | Determinability Ω* from threshold rules (±1 g, > 2 g, 150 lux) | Ω* derived from the **staging log** by rules committed as code before capture (Section 4) |
| A5 | Fixed 2 g weight threshold, shared by the scoring rule and Condition D | Weight test uses per-scale noise from scale characterisation; fitted on the calibration split only |
| A6 | Conditions A–D presented to reviewers | Methods compared automatically: TriNetra-Link vs. five baselines, plus ablations and robustness tests |
| A7 | Gates E-1, E-2, E-3 | Gates G-1 to G-4 (Section 6) |

**Unchanged:** the CP1–CP4 checkpoint definitions; the `ATTR_*` and `DEC_*` label codes; the separation of stage attribution from operational decision; the two abstention classes; SHA-256 commitment of the truth ledger before capture.

## 3. Scope after amendment

- **Primary (E1):** stage accuracy on determinable journeys and appropriate-abstention rate (AAR) on non-determinable journeys, TriNetra-Link vs. baselines B1–B5, on the 96-journey test split, with journey-level bootstrap 95% CIs and exact McNemar tests.
- **Secondary (E2):** robustness under controlled perturbations of the real captures (dropped checkpoint, blur, darkening, scale drift).
- **Secondary (E3):** ablations (no quality gate; no visual reconciler; fixed 2 g threshold; deterministic vs. probabilistic rule).
- **Future work, not part of this study:** the human-adjudicator comparison of separate vs. linked evidence. If it is run later, participants are ordinary consenting volunteers (students or logistics staff). No certification is needed; it requires informed consent, ideally institutional ethics approval, and **at least 16 participants**, because the participant is the unit of analysis.

## 4. Ground truth and determinability without reviewers

### 4.1 Roles

| Role | Does | Must not |
|---|---|---|
| **Stager** | Prepares each package, performs the assigned manipulation under a fixed overhead camera, fills the staging log | Capture checkpoint evidence for journeys they staged (when a second person is available) |
| **Capturer** | Records CP1–CP4 with the app following the capture SOP | See the assignment sheet or staging log |
| **Analyst** | Runs code; may be the stager or capturer | Change rules, thresholds or labels after looking at test results |

**Minimum team: two people** (stager ≠ capturer). With only one person available, use the single-person procedure (4.4) and disclose it as a limitation.

### 4.2 Staging log (one row per journey, written at staging time)

`journey_code, assigned_cell, actual_manipulation, manipulation_interval (S1|S2|S3|none), degraded_checkpoint (none|CP1..CP4), degradation_type (dark|scale_error|blur|missing), glare_over_defect (yes|no), overhead_video_file, overhead_video_sha256, deviation_notes, stager_id, timestamp_utc`

The **actual** manipulation and interval are the ground truth, not the intended cell. Deviations are logged, never corrected afterwards.

### 4.3 Determinability rule (code committed and hashed before capture)

| Staging log says | Ω* | Correct output |
|---|---|---|
| No manipulation, no degradation | DET | `ATTR_CONFIRMED_LEGITIMATE` |
| Manipulation in S_k, both bounding checkpoints usable, defect not hidden | DET | the matching stage label |
| A checkpoint bounding the manipulation interval deliberately degraded, or found unusable by the capture-quality check | DEG | `ATTR_ABSTAIN_DEGRADED` |
| Defect deliberately hidden by glare at both bounding checkpoints | IND | `ATTR_ABSTAIN_INDISTINGUISHABLE` |

*Usable* means the capture-quality check passes: the app recorded no scale error code, at least three weight readings exist, and the image luminance and blur metrics computed by the committed script are above fixed floors. **These floors are set from the 10-journey pilot (Gate G-3) and frozen before the main study. They are not the method's tuned thresholds.**

Optional audit: a second team member independently applies the written rule to a random 25% of journeys from the raw evidence. Report Cohen's κ. This needs no certification; it checks that the rule is applied consistently.

### 4.4 Single-person procedure (only if no second person is available)

1. A script prints 120 random journey codes and the cell assignment into a sealed sheet.
2. Stage all packages for a batch in one session, film each manipulation, and attach only the random code label.
3. Shuffle the batch physically before capture, and capture strictly by the SOP (fixed angles, fixed photo count, three weighings) without consulting the sheet.
4. Disclose in the paper that staging and capture were done by the same person, and that the automatic method, not the person, produces every prediction.

## 5. Sample and assignment

| Cell | Ground-truth interval | n |
|---|---|---|
| Intact | none | 30 |
| Permitted flyer-bag change (logged tare change) | none | 12 |
| Forward-transit damage | S1 | 14 |
| Doorstep substitution | S1 (at K = 4) | 14 |
| Customer tamper | S2 | 14 |
| Reverse-transit tamper | S3 | 12 |
| Degraded evidence | interval as staged, Ω* = DEG | 12 |
| Ambiguous evidence (glare) | interval as staged, Ω* = IND | 12 |
| **Total** | | **120** |

Assignment uses a seeded script. The calibration split is 24 journeys, stratified by cell; the test split is 96. Journey order is shuffled, so no batch is made of one cell.

## 6. Gates (replace E-1 to E-3)

| Gate | Requirement | Blocks |
|---|---|---|
| **G-1** | This amendment committed and tagged `v2.6.0-amendment` | Staging |
| **G-2** | Truth-ledger commitment manifest for the 120 journeys committed (salted SHA-256), and the determinability rule code committed with its hash | Capture |
| **G-3** | 10-journey pilot completed (excluded from analysis): app, scale and SOP work end-to-end; quality floors frozen | Main study |
| **G-4** | Scale characterisation completed (≥ 3 loads × 30 readings per scale) and `scales.json` committed | Threshold fitting |

## 7. Wording for the paper

> "The preregistered protocol (v2.5) was amended before any data were collected (v2.6, tagged in the public repository). The amendment withdrew a human-reviewer calibration gate that supported a human-adjudicator comparison, which is deferred to future work, and replaced reviewer-based determinability with labels derived from the filmed staging log by rules committed before capture."
