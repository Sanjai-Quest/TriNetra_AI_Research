# Standard Operating Procedure (SOP): Physical Package Staging & Manipulation

**Protocol Amendment:** v2.6.0  
**Gate Requirement:** Gate G-1 & G-2  
**Target Cohort:** $N = 120$ physical journeys across 8 scenario cells

---

## 1. Principles & Roles Separation

To guarantee experimental validity and eliminate investigator bias, strict role blinding is maintained during physical parcel manipulation:

| Role | Responsibilities | Mandatory Restrictions |
|---|---|---|
| **Stager** | Prepares physical parcel, performs assigned manipulation under continuous overhead video, attaches journey barcode, fills staging log. | **Must NOT** capture checkpoint evidence with the mobile app for journeys they staged (when a second person is available). |
| **Capturer** | Records CP1–CP4 checkpoints using the mobile web app following `docs/capture_SOP.md`. | **Must NOT** see the assignment sheet, staging log, or overhead video. |
| **Analyst** | Executes algorithmic evaluation pipelines. | **Must NOT** modify thresholds, rules, or labels after unblinding test results. |

*Single-Person Procedure:* If only one operator is available, all parcels must be staged, sealed, and randomized in one session before physical shuffling and subsequent capture per Amendment v2.6 §4.4.

---

## 2. Overhead Video Recording Protocol

1. **Camera Position:** Mount a fixed high-resolution camera directly above the staging workbench with clear, unobstructed visibility of the entire package and operator hands.
2. **Lighting:** Minimum 500 lux uniform diffuse lighting across the workbench surface.
3. **Session Procedure:**
   - Position parcel on workbench with journey code label visible.
   - Start overhead video recording.
   - Read journey code aloud into microphone.
   - Execute the assigned physical manipulation exactly as prescribed.
   - Show all manipulated surfaces and resealed security tape to the overhead lens.
   - Conclude recording.
4. **Cryptographic Integrity:** Compute SHA-256 digest of the raw video file immediately after recording:
   ```bash
   sha256sum video_JRN_2026_xxxx.mp4
   ```
   Record filename and SHA-256 hash into the staging log.

---

## 3. Protocol for the 8 Scenario Cells

### Cell 1: Intact Legitimate Transit ($n=30$)
- **Interval:** None (`none`).
- **Action:** Inspect standard sealed carton. Weigh baseline. Apply primary tamper-evident security tape. Package undergoes legitimate simulated handling without breach.

### Cell 2: Permitted Flyer-Bag Change ($n=12$)
- **Interval:** None (`none`).
- **Action:** At transit stage (between CP1 and CP2), legitimate logistics flyer bag is applied (+15.0g tare delta). The change is officially logged via `permitted_packaging_change=True` with explicit tare adjustment. Internal security seal remains intact.

### Cell 3: Forward-Transit Damage ($n=14$)
- **Interval:** Stage 1 ($S_1$, between CP1 and CP2).
- **Action:** Subject carton edge to 5mm mechanical puncture/compression under camera, simulating transit drop impact. Structural tear visible on front/side face.

### Cell 4: Doorstep Substitution ($n=14$)
- **Interval:** Stage 1 ($S_1$ at delivery point $K=4$).
- **Action:** Slit base of carton carefully, remove serialized primary item, substitute with inert mass surrogate (-35.0g discrepancy). Reseal using non-matching standard tape.

### Cell 5: Customer Tamper ($n=14$)
- **Interval:** Stage 2 ($S_2$, between CP2 carrier facility and CP3 return doorstep).
- **Action:** Slit security seal tape, replace original unit with counterfeit/depleted hardware. Apply non-matching replacement seal QR code.

### Cell 6: Reverse-Transit Carrier Tamper ($n=12$)
- **Interval:** Stage 3 ($S_3$, between CP3 return pickup and CP4 return hub).
- **Action:** Slit carton tape during reverse transit leg, extract accessories/components, re-tape with secondary clear adhesive.

### Cell 7: Degraded Evidence ($n=12$)
- **Interval:** Staged tamper at $S_2$, with bounding checkpoint (CP2 or CP3) deliberately degraded:
  - Sub-condition 7a: Scale error simulated (scale status set to ERROR / unstable reading).
  - Sub-condition 7b: Severe underexposure (< 15 lux, gamma darkened).
  - Sub-condition 7c: Severe camera defocus blur ($\sigma \ge 4.0$).
- **Determinability Ground Truth:** $\Omega^* = \text{OBS\_DEGRADED\_INCOMPLETE} \implies \text{ATTR\_ABSTAIN\_DEGRADED}$.

### Cell 8: Ambiguous Evidence via Deliberate Glare ($n=12$)
- **Interval:** Staged tamper at $S_2$, with specular reflection deliberately directed across the security seal tape at bounding checkpoints:
  - Specular glare angle aligned so seal text / micro-patterns are washed out (> 20% specular saturation).
- **Determinability Ground Truth:** $\Omega^* = \text{OBS\_INDISTINGUISHABLE} \implies \text{ATTR\_ABSTAIN\_INDISTINGUISHABLE}$.

---

## 4. Staging Log Entry

Immediately following staging of each package, append a record via the TriNetra CLI:

```bash
trinetra staging log \
  --journey-code "JRN-2026-0001" \
  --cell "customer_tamper" \
  --manipulation "Slit top seal tape, substituted unit, applied counterfeit seal" \
  --interval "S2" \
  --stager-id "STAGER_01" \
  --video-file "video_JRN_2026_0001.mp4" \
  --video-sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
```

The physical record is committed into access-controlled `data/restricted/staging_log_120.csv`. Deviations from intended cells are logged, never erased or overwritten.
