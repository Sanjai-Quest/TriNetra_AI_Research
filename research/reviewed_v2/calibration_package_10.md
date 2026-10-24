# TriNetra AI: 10-Case Reviewer Calibration System (Gate E-3 Master Protocol)

> **Document Type:** Master Calibration Protocol & Access Control Directory  
> **Protocol Version:** 2.5.0  
> **Target Gate:** Pre-Execution Gate E-3 (Reviewer Calibration Trial)  
> **Gate Status:** PENDING / UNEXECUTED (Do NOT Fabricate Results or Assume Passed)  
> **Date:** 2026-10-24  

---

## 1. Calibration Architecture & Material Separation

To maintain strict scientific blinding and prevent reviewers from viewing answers prior to evaluation, calibration materials are strictly separated into two decoupled artifacts:

```
┌────────────────────────────────────────────────────────────────────────┐
│ [REVIEWER-FACING MATERIAL] Open to Reviewers R1, R2, R3, R4            │
│ • File: calibration_reviewer_pack_10.md                                │
│ • Contents: Rubric instructions, dropdown definitions, and 10 benchmark │
│   cases presenting ONLY observable sensory evidence under Condition D.  │
│ • Response Template: calibration_ratings_template.csv (Blank)          │
│ • ZERO disclosure of ground-truth labels or normative answers.         │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [RESTRICTED MASTER KEY] Trial Coordinator Only (Embargoed)             │
│ • File: calibration_answer_key_restricted.md                           │
│ • Contents: Unblinded physical ground truth, target observability,     │
│   normative attributions, normative platform decisions, and rationale. │
│ • Access: STRICTLY WITHHELD FROM REVIEWERS until calibration is done.   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory of Calibration Artifacts

1. **Reviewer Case Pack:**  
   [`calibration_reviewer_pack_10.md`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/TriNetra_Mobile/research/reviewed_v2/calibration_reviewer_pack_10.md)  
   *Distribute to Reviewers $R_1, R_2, R_3, R_4$ at the start of the calibration session.*
2. **Blank Evaluation Form Template:**  
   [`calibration_ratings_template.csv`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/TriNetra_Mobile/research/reviewed_v2/calibration_ratings_template.csv)  
   *Reviewers submit their independent attribution and decision ratings here.*
3. **Restricted Answer Key & Scoring Guide:**  
   [`calibration_answer_key_restricted.md`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/TriNetra_Mobile/research/reviewed_v2/calibration_answer_key_restricted.md)  
   *Coordinator access only. Used to evaluate responses and compute Fleiss' $\kappa$.*

---

## 3. Calibration Execution Workflow (Gate E-3: Rubric & Agreement Calibration)

> [!IMPORTANT]
> **Scope of Gate E-3:** Gate E-3 is strictly a **text-based rubric and inter-reviewer agreement calibration** using the 10 benchmark case scenarios. It verifies consistent interpretation of the five-layer taxonomy and establishes baseline inter-rater agreement on case facts. It does **not** validate visual-interface proficiency.

1. **Reviewer Briefing:** Reviewers review Section 2 of `calibration_reviewer_pack_10.md` to understand the 5-layer taxonomy, attribution dropdown choices, and operational decision policies.
2. **Independent Adjudication:** Reviewers evaluate Cases $C_{01}$ through $C_{10}$ in `calibration_reviewer_pack_10.md` using the text-based case facts, photographic descriptions, and tare weight deltas, and enter their assessments into `calibration_ratings_template.csv`.
3. **Automated Reliability Check:** The trial coordinator ingests the completed ratings CSV and computes Fleiss' $\kappa$.
4. **Gate E-3 Clearance Standard:**  
   - **Passing Threshold:** Fleiss' $\kappa \ge 0.60$ (substantial agreement under Landis & Koch 1977).
   - If $\kappa \ge 0.60$, Gate E-3 is formally CLEARED.
   - If $\kappa < 0.60$, reviewers receive targeted re-training on discordant categories, followed by re-testing on an alternate 10-case battery.

---

## 4. Separate Unscored Interface Familiarization Step (Pre-Trial Tool Orientation)

Following successful clearance of Gate E-3 and immediately prior to Session 1 of the Latin Square trial, reviewers undergo a **separate, unscored interface familiarization step**:
- **Objective:** Allow reviewers to become comfortable with the interactive UI elements across all four experimental conditions:
  - Condition A: Single-point photo viewer and scale display;
  - Condition B: Two-tab navigation between dispatch and receiving;
  - Condition C: Four-tab unaligned record viewer;
  - Condition D: Unified chronological timeline, side-by-side synchronized pan/zoom viewer, and continuous tare weight curves.
- **Dedicated Orientation Materials:** Conducted using **2–3 dummy orientation walkthrough cases** (`ORIENT-01`, `ORIENT-02`, `ORIENT-03`).
- **Strict Prohibition on Experimental Stimuli:** **The 60 experimental package journeys ($J_{01}-J_{60}$) are STRICTLY FORBIDDEN from use in interface familiarization or practice**. Reviewers must have zero prior exposure to experimental package journeys.
- **Unscored:** No accuracy, attribution correctness, or latency metrics are recorded during this orientation.

---

## 5. Current Pre-Execution Gate Declaration

| Component | Target Criterion | Current Status |
|:---:|---|:---:|
| **E-3.1** | Reviewer Case Pack Prepared (Blinded) | **COMPLETED** ([`calibration_reviewer_pack_10.md`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/TriNetra_Mobile/research/reviewed_v2/calibration_reviewer_pack_10.md)) |
| **E-3.2** | Restricted Answer Key Prepared | **COMPLETED** ([`calibration_answer_key_restricted.md`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/TriNetra_Mobile/research/reviewed_v2/calibration_answer_key_restricted.md)) |
| **E-3.3** | Response Template Prepared | **COMPLETED** ([`calibration_ratings_template.csv`](file:///c:/Users/mitsu/Downloads/TriNetra_Mobile_FIXED/TriNetra_Mobile/research/reviewed_v2/calibration_ratings_template.csv)) |
| **E-3.4** | Text-Based Rubric Calibration Executed | **PENDING** |
| **E-3.5** | Multi-Rater Fleiss' $\kappa \ge 0.60$ | **PENDING / NOT CLEARED** |
| **E-3.6** | Unscored UI Familiarization Step | **PENDING (Scheduled Post-E-3)** |

**Overall Gate E-3 Status: PENDING / NOT CLEARED.** Execution remains frozen until human reviewers complete the calibration trial and achieve Fleiss' $\kappa \ge 0.60$.
