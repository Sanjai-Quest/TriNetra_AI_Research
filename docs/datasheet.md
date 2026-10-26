# Datasheet for Dataset: TriNetra Physical Supply-Chain Attribution Cohort

Standardized documentation following the *Datasheets for Datasets* framework (Gebru et al., *CACM* 2021).

---

## 1. Motivation

- **For what purpose was the dataset created?**  
  To evaluate algorithms for multimodal chain-of-custody verification and physical tamper attribution across supply chain transfer intervals. Unlike prior unimodal or synthetic benchmarks, TriNetra captures real-world physical manipulations under controlled laboratory conditions with rigorous sensor noise, packaging tare changes, and deliberate telemetry degradations.
- **Who created the dataset and who funded it?**  
  Created by the TriNetra-Link Research Initiative under Protocol Amendment v2.6.0.
- **What grant or institutional support funded it?**  
  Academic research initiative funded through institutional open-source logistics integrity grants.

---

## 2. Composition

- **What do the instances that comprise the dataset represent?**  
  Each instance represents a complete 4-checkpoint supply chain journey of a physical retail parcel:
  1. Intake Checkpoint 1 (CP1): Origin logistics fulfillment center.
  2. Transit Checkpoint 2 (CP2): Regional carrier distribution center.
  3. Handover Checkpoint 3 (CP3): Customer doorstep / return intake.
  4. Disposition Checkpoint 4 (CP4): Origin reverse return processing facility.
- **How many instances are there in total?**  
  - $N = 120$ physical evaluation journeys.
  - $N = 10$ pilot calibration journeys (`PILOT-01` .. `PILOT-10`, strictly excluded from all benchmarks).
  - Total checkpoint observations: 480 evaluation observations + 40 pilot observations.
- **What is the breakdown across scenario cells?**  
  The 120 evaluation journeys are partitioned across 8 canonical supply-chain scenario cells:
  1. `intact`: $n = 30$ (Legitimate transit, zero physical tampering).
  2. `permitted_flyer`: $n = 12$ (Legitimate logistics tare adjustment, +15.0g flyer-bag addition).
  3. `forward_transit_damage`: $n = 14$ (Mechanical carton breach in forward transit $S_1$).
  4. `doorstep_substitution`: $n = 14$ (Substituted item surrogate at customer delivery point $S_1$).
  5. `customer_tamper`: $n = 14$ (Item extracted / counterfeit seal applied during custody $S_2$).
  6. `reverse_transit_tamper`: $n = 12$ (Pilferage in reverse carrier leg $S_3$).
  7. `degraded_evidence`: $n = 12$ (Staged tamper with bounding checkpoint sensor failure or underexposure).
  8. `ambiguous_evidence`: $n = 12$ (Staged tamper with bounding checkpoints obscured by deliberate glare).
- **Does the dataset contain all possible instances or a sample?**  
  A representative balanced sample designed to stress-test multimodal attribution under both intact handling and sophisticated physical tampering.
- **What data does each instance contain?**  
  - Checkpoint metadata (device UUID, operator ID, timestamps in UTC).
  - Repeated digital weight readings (minimum 3 readings per checkpoint) and scale health status.
  - Security seal QR code payloads, serial numbers, and IMEI identifiers.
  - Multi-surface photographic evidence (TOP, FRONT, SEAL) with SHA-256 byte digests.

---

## 3. Collection Process

- **How were data collected?**  
  Physical packages were handled according to the Standard Operating Procedures (`docs/staging_SOP.md` and `docs/capture_SOP.md`).
- **What mechanisms were used to record data?**  
  - Handheld mobile web capture client (`trinetra_link/ingest/static/capture.html`) connected to FastAPI server.
  - Digital commercial bench scales characterized for empirical Gaussian noise $\sigma$ and linearity drift $\delta$.
  - Continuous overhead 1080p video recording of all staging manipulations.
- **Who was involved in the data collection process?**  
  Trained physical staging operators (Stager role) and independent mobile app capture operators (Capturer role) operating under double-blind protocol separation.

---

## 4. Preprocessing, Cleaning & Labeling

- **Was any preprocessing/cleaning done?**  
  Photographic evidence is preserved as raw captures alongside normalized 4-corner planar homography projections. Scale readings are preserved as raw floats.
- **How was ground truth determined?**  
  Under Protocol Amendment v2.6.0, ground truth does not rely on subjective human reviewers. It is derived deterministically from the filmed physical staging log via code committed to the repository before capture starts (Gate G-2):
  - Determinability $\Omega^* \in \{\text{OBS\_DETERMINABLE}, \text{OBS\_DEGRADED\_INCOMPLETE}, \text{OBS\_INDISTINGUISHABLE}\}$.
  - Ground-truth stage label $\in \{\text{ATTR\_CONFIRMED\_LEGITIMATE}, \text{ATTR\_STAGE(1)}, \text{ATTR\_STAGE(2)}, \text{ATTR\_STAGE(3)}, \text{ATTR\_ABSTAIN\_DEGRADED}, \text{ATTR\_ABSTAIN\_INDISTINGUISHABLE}\}$.
- **Was a commitment procedure used?**  
  Yes. Prior to study capture, a cryptographic salted SHA-256 commitment manifest (`research/truth_manifest_v2.6.json`) was generated and committed alongside the determinability rule code hash.

---

## 5. Uses

- **Has the dataset been used for tasks before?**  
  Used to evaluate the TriNetra-Link framework against 5 baseline methods (B1: CP4-only, B2: Endpoints, B3: Unlinked first-detection, B4: Groq LLM Judge, B5: Ported V3 rules), controlled sensor perturbations (E2), and architectural ablations (E3).
- **What tasks should the dataset NOT be used for?**  
  Not intended for end-consumer facial or biometric identification (no human identifiable faces or personal data are recorded).

---

## 6. Distribution & Maintenance

- **How is the dataset distributed?**  
  Distributed under the Open Data Commons / Creative Commons Attribution 4.0 International (CC BY 4.0) license. Staging sheets and ground truth files are embargoed in `data/restricted/` to preserve double-blinding during blind evaluations.
- **Who maintains the dataset?**  
  The TriNetra Open Science Working Group via GitHub repository issues and releases.
