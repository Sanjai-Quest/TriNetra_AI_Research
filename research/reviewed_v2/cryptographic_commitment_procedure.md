# TriNetra AI: Cryptographic Pre-Commitment & Blinding Procedure (Gate E-2)

> **Document Type:** Standard Operating Procedure (SOP) & Blinded Verification Standard  
> **Protocol Version:** 2.5.0  
> **Target Manifest:** `ground_truth_commitment_manifest.json`  
> **Embargo Target:** `ground_truth_ledger_60.csv` (Access-Controlled / Embargoed)  
> **Gate Status:** PENDING FINAL HUMAN SIGN-OFF (DO NOT COMMIT HASH UNTIL FINALIZED)  
> **Date:** 2026-10-24  

---

## 1. Objective and Protocol Rationale

In experimental forensics and return fraud adjudication research, **pre-commitment of ground-truth state assignments** is essential to prevent p-hacking, post-hoc scenario reclassification, and outcome manipulation. 

Simultaneously, **absolute reviewer blinding must be maintained**:
- If the plaintext ground-truth ledger is published directly to the public Git repository or public OSF registry, human reviewers could inspect the repository and discover the ground-truth answers for each package journey prior to adjudication.
- Therefore, Gate E-2 enforces a **cryptographic hash pre-commitment with an embargoed / access-controlled ledger**.

Under Pre-Execution Gate E-2 of the TriNetra Experimental Protocol:
1. The planned physical staging configuration, nominal weights, planned target checkpoint weights, and normative operational actions for all 60 package journeys are locked in `ground_truth_ledger_60.csv`.
2. A **SHA-256 cryptographic hash** of `ground_truth_ledger_60.csv` is computed and recorded in a public commitment manifest (`ground_truth_commitment_manifest.json`).
3. The **public Git repository and public pre-registration registry receive ONLY the preregistration protocol and the commitment manifest containing the SHA-256 hash**.
4. The readable ground-truth ledger `ground_truth_ledger_60.csv` is **STRICTLY EMBARGOED / ACCESS-CONTROLLED** (e.g. held in a private coordinator repository or an OSF Embargoed Component) until all four human reviewers complete all 240 evaluations across all Latin Square sessions.
5. Case IDs visible to human reviewers in evaluation sessions are randomized, blinded tracking codes (`CASE-XXXX`), preventing any deduction of scenario mappings.

> [!WARNING]
> **GOVERNANCE RESTRICTION:**  
> In accordance with project governance, **DO NOT commit or publish the final cryptographic hash until physical scenario definitions and staging targets are formally signed off**. Furthermore, **NEVER push `ground_truth_ledger_60.csv` to a public repository prior to completion of reviewer adjudication**.

---

## 2. Reviewer Blinding & Case Anonymization Architecture

To eliminate experimental bias and prevent reviewers from reverse-engineering ground truth:

```
┌────────────────────────────────────────────────────────────────────────┐
│ [PUBLIC ACCESS] Public Git Repository & OSF Public Preregistration     │
│ • preregistration_protocol_v2.5.md (Study design & hypotheses)         │
│ • revised_experiment_protocol.md (Methodological framework)            │
│ • ground_truth_commitment_manifest.json (SHA-256 hash manifest)        │
│ • calibration_reviewer_pack_10.md (Reviewer calibration materials)     │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [RESTRICTED ACCESS] Trial Coordinator Enclave (Embargoed Until Locked) │
│ • ground_truth_ledger_60.csv (Plaintext 60-journey truth assignments)  │
│ • calibration_answer_key_restricted.md (Calibration answer key)        │
│ • Randomization Key Table: maps journey_id (J01-J60) ↔ CASE-XXXX       │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [REVIEWER INTERFACE] Double-Blinded Evaluation Sessions               │
│ • Reviewers see ONLY: CASE-B1-01 through CASE-B4-15                    │
│ • Reviewers NEVER see J01-J60 or scenario block labels                 │
│ • Zero access to truth ledger, staging blueprints, or answer keys      │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Randomized Case Tracking IDs:**  
   During experimental sessions, packages are presented under randomized, blinded tracking identifiers (e.g., `CASE-B1-01` to `CASE-B4-15`). Reviewers are never shown internal sequential IDs ($J_{01}-J_{60}$).
2. **Independent Trial Coordinator:**  
   Physical staging, blinding key management, and ledger custody are handled by an independent trial coordinator who does NOT participate as an adjudicator.
3. **Embargo Period:**  
   The readable ledger remains strictly embargoed until all 240 evaluation forms are submitted and cryptographically timestamped.

---

## 3. Pre-Commitment File Audit Checklist

Before computing the final SHA-256 hash, verify that `ground_truth_ledger_60.csv` satisfies all structural constraints:

- [ ] **Row Count:** Exactly 60 data rows and 1 header row (total 61 lines).
- [ ] **Journey Sequence:** Continuous, monotonic IDs from `J01` through `J60`.
- [ ] **Field Separation:** Checkpoint columns explicitly designated as planned staging targets (`planned_cp1_target_weight_g`, etc.), completely separate from empirical measurements.
- [ ] **Cell Allocation Fidelity:**
  - `SC-01` (Standard Intact): Exactly 15 journeys ($J_{01}-J_{15}$).
  - `SC-02` (Permitted Bag Change): Exactly 8 journeys ($J_{16}-J_{23}$).
  - `SC-03` (Forward Transit Damage): Exactly 8 journeys ($J_{24}-J_{31}$).
  - `SC-04` (Doorstep Substitution): Exactly 8 journeys ($J_{32}-J_{39}$).
  - `SC-05` (Customer Tamper): Exactly 8 journeys ($J_{40}-J_{47}$).
  - `SC-06` (Reverse Transit Tamper): Exactly 5 journeys ($J_{48}-J_{52}$).
  - `SC-07` (Degraded Customer Tamper): Exactly 4 journeys ($J_{53}-J_{56}$).
  - `SC-08` (Ambiguous Customer Tamper): Exactly 4 journeys ($J_{57}-J_{60}$).
- [ ] **Observability Symmetry:** Verified that $\Omega_{iC}^* = \Omega_{iD}^*$ for all 60 rows.
- [ ] **Line Endings & Encoding:** Clean Unix line endings (`LF`, `\n`) and standard `UTF-8` encoding.

---

## 4. Step-by-Step SHA-256 Hash Computation

### 4.1 Windows PowerShell Execution
```powershell
# 1. Verify file line count
(Get-Content .\research\reviewed_v2\ground_truth_ledger_60.csv).Count
# Expected output: 61

# 2. Compute SHA-256 hash of the embargoed 60-journey truth ledger
$LedgerHash = Get-FileHash -Path .\research\reviewed_v2\ground_truth_ledger_60.csv -Algorithm SHA256
Write-Host "Embargoed Ground-Truth Ledger SHA-256:" $LedgerHash.Hash

# 3. Compute SHA-256 hash of the preregistration protocol
$ProtocolHash = Get-FileHash -Path .\research\reviewed_v2\preregistration_protocol_v2.5.md -Algorithm SHA256
Write-Host "Preregistration Protocol SHA-256:" $ProtocolHash.Hash
```

### 4.2 Unix / Linux / macOS Execution
```bash
# 1. Verify line count
wc -l research/reviewed_v2/ground_truth_ledger_60.csv
# Expected output: 61

# 2. Compute SHA-256 hashes
sha256sum research/reviewed_v2/ground_truth_ledger_60.csv
sha256sum research/reviewed_v2/preregistration_protocol_v2.5.md
```

---

## 5. Standardized Public Manifest & Blinded Git Commit Recipe

Upon final approval, the trial coordinator creates the public commitment manifest and commits ONLY public, blinded files:

### 5.1 Format of Public Commitment Manifest (`ground_truth_commitment_manifest.json`)
```json
{
  "manifest_version": "2.5.0",
  "document_type": "TriNetra Ground-Truth Cryptographic Commitment Manifest",
  "commitment_timestamp_utc": "<ISO_8601_TIMESTAMP>",
  "hash_algorithm": "SHA-256",
  "target_artifacts": [
    {
      "file_name": "ground_truth_ledger_60.csv",
      "sha256_hash": "<INSERT_COMPUTED_LEDGER_HASH_HERE>",
      "access_status": "RESTRICTED_EMBARGOED",
      "embargo_release_condition": "Completion of all 240 human reviewer adjudication evaluations across Latin Square sessions 1-4"
    },
    {
      "file_name": "preregistration_protocol_v2.5.md",
      "sha256_hash": "<INSERT_COMPUTED_PROTOCOL_HASH_HERE>",
      "access_status": "PUBLIC_OPEN_ACCESS"
    }
  ],
  "governance_attestation": "Ground-truth assignments locked prior to physical package staging. Plaintext ledger withheld from public repository to maintain reviewer blinding."
}
```

### 5.2 Public Git Commit Commands (Ledger Withheld)
```bash
# 1. Add ONLY public, blinded artifacts
git add research/reviewed_v2/preregistration_protocol_v2.5.md
git add research/reviewed_v2/revised_experiment_protocol.md
git add research/reviewed_v2/ground_truth_commitment_manifest.json
git add research/reviewed_v2/calibration_reviewer_pack_10.md

# 2. Explicitly ensure plaintext truth ledger is NOT staged
git reset research/reviewed_v2/ground_truth_ledger_60.csv
git reset research/reviewed_v2/calibration_answer_key_restricted.md

# 3. Create public commit with pre-commitment manifest
git commit -m "feat(research): pre-commit SHA-256 truth manifest and lock protocol v2.5.0

Public Pre-Registration SHA-256 Manifest:
- Preregistration Protocol: <INSERT_PROTOCOL_HASH>
- Embargoed Truth Ledger Hash: <INSERT_LEDGER_HASH> (plaintext ledger embargoed for reviewer blinding)

Pre-Execution Gate Status: E-1 and E-2 Manifest Locked
Trial Status: Execution FROZEN pending E-3 calibration and E-4 Elia et al. review"

# 4. Create signed Git tag
git tag -s v2.5.0-preregistration -m "TriNetra Phase 1 Pilot Pre-Registration Manifest Lock"
```

---

## 6. Post-Trial Unblinding & Verification Standard

1. **Trial Completion Trigger:** When all four reviewers submit their final Block 4 evaluations, the coordinator timestamps and locks the evaluation ratings database.
2. **Embargo Lift:** The trial coordinator publishes `ground_truth_ledger_60.csv` to the public repository.
3. **Automated Verification:**
   ```python
   import hashlib, json
   manifest = json.load(open("ground_truth_commitment_manifest.json"))
   expected_hash = manifest["target_artifacts"][0]["sha256_hash"]
   actual_hash = hashlib.sha256(open("ground_truth_ledger_60.csv", "rb").read()).hexdigest()
   assert actual_hash == expected_hash, "TAMPER DETECTED: Ground truth ledger does not match pre-committed hash!"
   print("SUCCESS: Ground-truth ledger verified authentic against pre-trial commitment manifest.")
   ```
4. If the hash matches, automated unblinding and scoring proceed. If the hash fails, the trial results are declared void.

---

## 7. Current Gate Status

| Gate | Description | Current Status | Action Required to Clear |
|:---:|---|:---:|---|
| **E-1** | Protocol Pre-Registration | **PENDING** | Execute Git commit and public OSF registration of protocol |
| **E-2** | Truth Ledger Hash Manifest | **PENDING** | Generate `ground_truth_commitment_manifest.json` with SHA-256 hash upon stakeholder sign-off (ledger embargoed) |
