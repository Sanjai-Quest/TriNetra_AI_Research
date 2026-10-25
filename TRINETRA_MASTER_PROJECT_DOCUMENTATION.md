# TriNetra AI
## Master Project Documentation

**Document version:** 1.0  
**Document date:** 2026-09-06  
**Project type:** Evidence capture, reconciliation, and dispute decision-support platform  
**Primary repository:** `TriNetra_Mobile`  
**Target users:** Courier and warehouse operators on mobile devices; investigators on laptop browsers

---

## 1. Executive Summary

TriNetra AI is a cross-organizational evidence reconciliation platform for e-commerce delivery, return, and refund disputes. It collects evidence from the physical supply chain and compares that evidence using deterministic, explainable rules.

The system is designed around one principle:

> TriNetra identifies evidence conflicts and evidence gaps. It does not determine a person's intent or label a person as fraudulent.

The project combines:

- An Android edge client for offline-first field capture.
- A standalone Spring Boot verdict backend for the working mobile demo.
- A Phase 1 Python research engine for normalization, entity resolution, reconciliation, and evaluation.
- A Phase 2 event-driven platform with claims, evidence, computer vision, fraud signals, verdict generation, and investigator workflows.
- A Phase 3 hardening layer with migrations, resilience, metrics, logging, and load testing.
- Public datasets, synthetic complaint fixtures (quarantined per audit), synthetic lifecycle test data, and reproducibility reports.

The implemented repository contains both a compact demonstration path and a larger enterprise-oriented reference implementation. They share the same evidence-reconciliation concept but are not a single automatically connected runtime.

---

## 2. Product Scope

### 2.1 Problem

E-commerce dispute evidence is fragmented across merchants, warehouses, carriers, return centers, and consumers. A single organization may see only one part of the product lifecycle. This creates disputes such as:

- Wrong or counterfeit item received.
- Empty-box or missing-item claims.
- Weight loss between dispatch and return.
- Damaged or pre-worn products.
- Invalid or contradictory delivery and return timestamps.
- Refunds withheld despite incomplete evidence.

### 2.2 Product Goal

TriNetra creates a common evidence record, compares independent signals, and produces an auditable result for human review.

### 2.3 In Scope

- Offline mobile evidence capture.
- Voice-to-structured observation parsing.
- BLE scale telemetry.
- Camera-based surface analysis.
- Evidence uploads and artifact processing.
- SKU, weight, variant, and timestamp reconciliation.
- Rule-based fraud signals.
- Claim queues and investigator overrides.
- Audit-oriented reasoning and test reports.

### 2.4 Out of Scope

- Autonomous accusations about customer intent.
- Payment gateway authorization or chargeback processing.
- Route navigation.
- A production-grade identity/KYC provider integration.
- Guaranteed truth from an individual image, voice statement, or sensor reading.

---

## 3. Repository Map

| Area | Purpose |
|---|---|
| [android/app](android/app) | Kotlin Android edge client using Compose, Room, WorkManager, CameraX, BLE, and local processing. |
| [backend](backend) | Standalone Spring Boot verdict engine used by the mobile demonstration path. |
| [TriNetra AI/phase-1](TriNetra%20AI/phase-1) | Research MVP, canonical normalization, entity resolution, reconciliation, baselines, and evaluation. |
| [TriNetra AI/phase-2/services](TriNetra%20AI/phase-2/services) | FastAPI services for claim, evidence, multimodal, fraud, verdict, and integration workflows. |
| [TriNetra AI/phase-2/spring-services](TriNetra%20AI/phase-2/spring-services) | Spring Boot service implementation for Phase 2 and Phase 3 hardening. |
| [TriNetra AI/phase-2/frontend-react](TriNetra%20AI/phase-2/frontend-react) | React investigator dashboard. |
| [TriNetra AI/phase-3](TriNetra%20AI/phase-3) | Load testing, operational hardening, migrations, observability, and resilience. |
| [datasets](datasets) | Synthetic complaint fixtures and taxonomies (QUARANTINED per audit; see datasets/QUARANTINE.md). |
| [testing](testing) | Synthetic, real-world, performance, demo, and validation outputs. |
| [TriNetra AI/research](TriNetra%20AI/research) | Literature, claims, experiment, figure, and research traceability assets. |
| [TRINETRA_COMPREHENSIVE_SPECIFICATION.md](TRINETRA_COMPREHENSIVE_SPECIFICATION.md) | Product and technical blueprint. |
| [trinetra_master_production_blueprint.md](trinetra_master_production_blueprint.md) | Extended architecture and user workflow blueprint. |

Generated directories such as Android `build`, Maven `target`, Gradle caches, Python bytecode, and frontend dependency folders are build artifacts rather than source-of-truth implementation.

---

## 4. System Context: Two-Sided Window

TriNetra has two primary operating windows. They are deliberately different because the users, environment, and time available for interaction are different.

### 4.1 Mobile Window: Capture and Handoff

**Primary users:** couriers, warehouse operators, return-dock inspectors, and field staff.

**Operating environment:**

- Bright outdoor or warehouse lighting.
- Glare, noise, movement, and gloves.
- Basement, elevator, and low-connectivity areas.
- Seconds rather than minutes per transaction.
- Physical packages and scales in the user's hands.

**Mobile responsibilities:**

1. Identify or scan a package/seal.
2. Capture a spoken observation or typed transcript.
3. Record local telemetry and timestamps.
4. Read or receive physical measurements.
5. Run lightweight local CV/NLP processing.
6. Store the evidence packet locally when offline.
7. Synchronize the packet when connectivity returns.

**Mobile interaction model:**

- Large, direct actions.
- Minimal data entry.
- Clear progress states: idle, recording, processing, success, error.
- Offline queue visibility.
- Evidence capture before network synchronization.

The current Android implementation is in [HandoffScreen.kt](android/app/src/main/java/com/trinetra/ai/ui/handoff/HandoffScreen.kt), [HandoffViewModel.kt](android/app/src/main/java/com/trinetra/ai/ui/handoff/HandoffViewModel.kt), and [MainActivity.kt](android/app/src/main/java/com/trinetra/ai/MainActivity.kt).

### 4.2 Laptop Window: Investigation and Decision

**Primary users:** fraud analysts, customer-support investigators, operations managers, and compliance reviewers.

**Operating environment:**

- Desk-based review.
- Multiple claims and evidence records.
- Need for comparison, filtering, reasoning, and audit history.
- Larger display and keyboard/mouse input.
- More time for human judgment.

**Laptop responsibilities:**

1. Search and filter the investigation queue.
2. Open a complete claim record.
3. Review fraud signals and confidence values.
4. Read automated reasoning and evidence summaries.
5. Inspect the audit trail.
6. Apply a justified manual override.
7. Refresh the queue as processing completes.

The dashboard is implemented in [App.tsx](TriNetra%20AI/phase-2/frontend-react/src/App.tsx), [ClaimQueue.tsx](TriNetra%20AI/phase-2/frontend-react/src/components/ClaimQueue.tsx), [ClaimDetailView.tsx](TriNetra%20AI/phase-2/frontend-react/src/components/ClaimDetailView.tsx), and [VerdictOverrideModal.tsx](TriNetra%20AI/phase-2/frontend-react/src/components/VerdictOverrideModal.tsx).

### 4.3 Mobile-to-Laptop Handoff

```text
Physical observation
        |
        v
Android capture and local parsing
        |
        v
Room offline telemetry record
        |
        v
WorkManager synchronization
        |
        v
Claim/evidence backend
        |
        v
CV processing + fraud signals + reconciliation
        |
        v
Laptop investigator queue
        |
        v
Human review, override, and audit record
```

The mobile application captures facts close to the physical event. The laptop application provides the context and control required for a defensible final decision.

---

## 5. Implemented Mobile Client

### 5.1 Application Shell

The Android app uses Kotlin, Jetpack Compose, Material 3, CameraX, Room, WorkManager, and Android permissions. Its entry point is [MainActivity.kt](android/app/src/main/java/com/trinetra/ai/MainActivity.kt).

The current navigation exposes:

- **Handoff:** package/seal observation and voice parsing.
- **CV Scan:** camera preview and live mathematical metrics.

Build and dependency configuration is in [android/app/build.gradle.kts](android/app/build.gradle.kts).

### 5.2 Voice Intake

[HandoffScreen.kt](android/app/src/main/java/com/trinetra/ai/ui/handoff/HandoffScreen.kt) uses the Android speech recognizer and supports a manually editable transcript. It sends the transcript to the ViewModel.

[HandoffViewModel.kt](android/app/src/main/java/com/trinetra/ai/ui/handoff/HandoffViewModel.kt) executes this order:

1. Try the configured Spring backend `/api/claims/voice/parse` endpoint.
2. Parse the structured response when the Groq path succeeds.
3. Fall back to [VoiceClassifier.kt](android/app/src/main/java/com/trinetra/ai/nlp/VoiceClassifier.kt) when the backend is unavailable.
4. Build a telemetry JSON packet.
5. Save the packet to Room.
6. Enqueue WorkManager synchronization.
7. Render a success or error state.

The local classifier is an honest CPU-bound weighted keyword classifier. It recognizes seal, light-weight, heavy-weight, and normal-condition indicators. It is not a Whisper, ONNX, or neural language model implementation.

### 5.3 Computer Vision

[CameraScreen.kt](android/app/src/main/java/com/trinetra/ai/ui/cv/CameraScreen.kt) provides a CameraX back-camera preview and displays live analysis metrics.

[OpenCVProcessor.kt](android/app/src/main/java/com/trinetra/ai/cv/OpenCVProcessor.kt) provides:

- Laplacian variance calculation.
- Sobel/Canny-style edge density calculation.
- Optional JNI native calls when `trinetra_opencv` is available.
- Pure Kotlin mathematical fallback when the native library is unavailable.

The current screen uses generated test frames for metric refresh rather than feeding actual camera frames into the analysis pipeline. Camera preview itself is real.

### 5.4 BLE Telemetry

[BluetoothScaleManager.kt](android/app/src/main/java/com/trinetra/ai/ble/BluetoothScaleManager.kt) implements:

- GATT callback scaffolding.
- Weight byte parsing.
- Sequence numbers.
- Pairing session identifiers.
- Timestamped telemetry packets.
- HMAC-SHA256 signatures.

The current scale ID, pairing session, and shared secret are demonstration values. Production deployment requires secure provisioning, key rotation, replay-window validation, and real scale characteristic discovery.

### 5.5 Offline Storage and Synchronization

The local persistence layer consists of:

- [TelemetryEntity.kt](android/app/src/main/java/com/trinetra/ai/data/local/TelemetryEntity.kt)
- [TelemetryDao.kt](android/app/src/main/java/com/trinetra/ai/data/local/TelemetryDao.kt)
- [AppDatabase.kt](android/app/src/main/java/com/trinetra/ai/data/local/AppDatabase.kt)
- [TelemetryUploadWorker.kt](android/app/src/main/java/com/trinetra/ai/data/sync/TelemetryUploadWorker.kt)

Room stores unsynchronized evidence records. WorkManager requires network connectivity, posts records to the backend, marks successful records as synchronized, and retries failed batches.

### 5.6 Mobile Limitations

The current implementation still uses demonstration values for GPS, seal IDs, claim metadata, and some backend payload fields. It also uses Android speech recognition rather than a bundled offline ASR model. These are implementation boundaries, not claims of full production hardware integration.

---

## 6. Implemented Standalone Backend

The root [backend](backend) is a compact Spring Boot 3.2 service using Java 21, JPA, PostgreSQL, H2 tests, and Lombok.

### 6.1 Verdict API

[VerdictController.java](backend/src/main/java/com/trinetra/verdict/controller/VerdictController.java) exposes:

| Endpoint | Purpose |
|---|---|
| `POST /api/claims/verdict` | Persist a claim/evidence packet and compute a verdict. |
| `POST /api/claims/telemetry` | Receive mobile telemetry synchronization payloads. |
| `POST /api/claims/voice/parse` | Forward a transcript to the configured Groq parser. |
| `GET /api/claims/{claimId}/verdict` | Recompute a stored claim's verdict. |

### 6.2 Deterministic Rules

[VerdictService.java](backend/src/main/java/com/trinetra/verdict/service/VerdictService.java) evaluates rules in this order:

1. Missing or mismatched outbound/return SKU -> `IDENTITY_CONFLICT`.
2. Return weight more than 5% below outbound weight -> `WEIGHT_ANOMALY`.
3. Return timestamp before delivery timestamp -> `TEMPORAL_CONFLICT`.
4. Fewer than two evidence records -> `MISSING_EVIDENCE`.
5. Otherwise -> `NONE`, described as consistent.

The first matching rule wins. Evidence payload contents are stored, but the compact backend primarily uses claim fields and evidence count for the final verdict.

### 6.3 Voice Parsing Boundary

[GroqService.java](backend/src/main/java/com/trinetra/verdict/service/GroqService.java) uses a low-temperature, JSON-constrained prompt for multilingual transcript extraction. Groq is an ingestion aid only in this path; final claim verdict computation remains in `VerdictService`.

### 6.4 Database

[backend/src/main/resources/schema.sql](backend/src/main/resources/schema.sql) defines claims, evidence, and verdicts and includes seeded scenarios for clean returns, weight anomalies, identity conflicts, temporal conflicts, and missing evidence.

---

## 7. Phase 1 Research Engine

Phase 1 is the scientific and algorithmic foundation. Its master runner is [generate_and_evaluate.py](TriNetra%20AI/phase-1/generate_and_evaluate.py).

### 7.1 Processing Pipeline

```text
Synthetic or real evidence
        |
        v
Canonical normalization
        |
        v
Entity resolution
        |
        v
Single-source baselines
        |
        v
Multi-source reconciliation
        |
        v
Metrics, ablation, confusion matrices, and reports
```

### 7.2 Normalization

[canonical_normalizer.py](TriNetra%20AI/phase-1/normalization/canonical_normalizer.py) standardizes:

- SKU formatting.
- Weight units to grams.
- Apparel sizes.
- Color names.
- Timestamp formats.

### 7.3 Entity Resolution

[entity_resolver.py](TriNetra%20AI/phase-1/resolution/entity_resolver.py) maps organization-specific identifiers to canonical product IDs. It supports explicit registry mappings and deterministic UUID generation when no mapping exists.

### 7.4 Reconciliation

[reconciliation_engine.py](TriNetra%20AI/phase-1/engine/reconciliation_engine.py) checks:

- Identity conflicts.
- Size and color variant conflicts.
- Weight drops above the research threshold.
- Three-sigma weight outliers.
- Lifecycle timestamp inversions.
- Missing custody sources.

The research engine returns status, recommendation, confidence, conflict details, source provenance, and missing-source information.

### 7.5 Research Evaluation

The synthetic generator creates 1,000 seeded cases: 900 normal lifecycles and 100 injected conflict cases. The evaluator compares identity-only, weight-only, timeline-only, and full reconciliation baselines.

The reported Phase 1 results are benchmark results on generated data. They demonstrate rule coverage and reproducibility; they do not establish live deployment accuracy.

---

## 8. Phase 2 Enterprise Platform

Phase 2 adds an event-driven architecture around PostgreSQL, Redis, RabbitMQ, MinIO, FastAPI, Spring Boot, and React.

### 8.1 Service Responsibilities

| Service | Port | Responsibility |
|---|---:|---|
| Claim service | 8080 | Claim creation, search, assignment, and overrides. |
| Evidence service | 8081 | File upload, MinIO storage, evidence records, and artifact retrieval. |
| Multimodal processor | 8082 | OpenCV wear metrics, EXIF extraction, color analysis, OCR, and receipt parsing. |
| Fraud engine | 8083 | Serial-return, fast-return, inflated-claim, cross-organization, and wardrobing signals. |
| Verdict generator | 8084 | Fraud-risk aggregation, Phase 1 reconciliation, verdict generation, and reasoning. |
| Integration service | 8085 | Carrier, payment, KYC, object-analysis, and dead-letter workflows. |
| React dashboard | 5173 or 3000 | Investigator queue, claim detail, reasoning, and overrides. |

### 8.2 Event Flow

```text
claim.created
      |
      v
evidence.uploaded
      |
      v
evidence.processed
      |
      v
fraud.analysis.complete
      |
      v
verdict.generated
```

RabbitMQ provides asynchronous decoupling. PostgreSQL stores the durable claim and evidence state. Redis caches customer patterns and verdicts. MinIO stores uploaded evidence objects.

### 8.3 Multimodal Processing

[phase-2/services/multimodal_processor/main.py](TriNetra%20AI/phase-2/services/multimodal_processor/main.py) implements deterministic image and document processing:

- OpenCV saturation, edge-density, and Laplacian features.
- EXIF extraction with Pillow.
- Dominant-color estimation.
- Receipt OCR through pytesseract when available.
- Receipt amount/date parsing.
- Artifact persistence.

These outputs are evidence artifacts and should be treated as signals requiring context, not absolute truth.

### 8.4 Fraud Signals

[phase-2/services/fraud_engine/main.py](TriNetra%20AI/phase-2/services/fraud_engine/main.py) identifies patterns such as:

- Seven or more returns in 90 days.
- Return initiated less than 60 minutes after delivery.
- Claim amount above 150% of product value.
- Multiple organizations or order patterns.
- Wear score at or above 0.70.

The signals feed the verdict workflow; they are not themselves proof of intent.

### 8.5 Verdict Generation

[phase-2/services/verdict_generator/main.py](TriNetra%20AI/phase-2/services/verdict_generator/main.py) combines fraud signals with Phase 1 reconciliation:

- Critical/high composite risk may result in `REJECT`.
- A reconciliation conflict or intermediate risk results in `INVESTIGATE`.
- Low risk and no conflict results in `REFUND`.

The service stores evidence summaries, signal contributions, confidence, and reasoning text. The dashboard exposes that reasoning to investigators.

### 8.6 Data Schema

[phase-2/schema/schema_extensions.sql](TriNetra%20AI/phase-2/schema/schema_extensions.sql) defines:

- `claims`
- `evidence`
- `evidence_artifacts`
- `fraud_signals`
- `verdict_reasoning`
- `investigator_actions`
- `integration_events`

The schema is designed to preserve both raw evidence references and derived reasoning.

---

## 9. Phase 3 Production Hardening

Phase 3 adds operational controls to the Spring service stack:

- Resilience4j circuit breakers and retries.
- Exponential retry backoff.
- Flyway database migrations.
- HikariCP pool configuration.
- Micrometer and Prometheus metrics.
- Structured JSON logging.
- Health and actuator endpoints.
- Global exception handling.
- Locust load tests.

The implementation and reported results are documented in [PHASE_3_RESULTS.md](TriNetra%20AI/phase-3/PHASE_3_RESULTS.md). Load-test claims should be interpreted as environment-specific benchmark evidence, not a universal production SLA guarantee.

---

## 10. Investigator Dashboard

The React dashboard is a laptop-oriented workspace for human review.

### Queue view

[ClaimQueue.tsx](TriNetra%20AI/phase-2/frontend-react/src/components/ClaimQueue.tsx) provides:

- Claim/order/category search.
- Status filtering.
- Verdict badges.
- Confidence display.
- Claim selection.

### Detail view

[ClaimDetailView.tsx](TriNetra%20AI/phase-2/frontend-react/src/components/ClaimDetailView.tsx) provides:

- Claim and customer context.
- Monetary metrics.
- Automated verdict and confidence.
- Fraud signal severity and reasoning.
- Automated reasoning text.
- Investigator action history.

### Human override

[VerdictOverrideModal.tsx](TriNetra%20AI/phase-2/frontend-react/src/components/VerdictOverrideModal.tsx) requires a justification of at least ten characters before sending an override to the Claim Service.

The dashboard is a decision-support surface. It does not remove the investigator from the loop.

---

## 11. Data and Research Assets

### Public macro data

The public datasets support the problem framing and national-scale complaint analysis. They are not direct labels for the reconciliation engine.

### Synthetic Complaint Corpus (Quarantined)

> [!CAUTION]
> **AUDIT FINDING (2026-10-23):** The 1,050-record complaint corpus in `datasets/` was template-generated by Python scripts (`expand_master_dataset.py`, `build_trinetra_1000_corpus.py`), not collected from live social platforms. Claims of "0% synthetic data" are retracted. All related CSVs are quarantined under [`datasets/QUARANTINE.md`](datasets/QUARANTINE.md).
>
> - Complaint narratives in this corpus are synthetic template variations, not verified physical ground truth.
> - Keyword classification cannot be used as an empirical fraud benchmark.
> - The reported backend comparison in previous validation reports was simulated when the backend was offline (retracted per Finding F-07).

### Synthetic Benchmark & Unit Test Suites

The synthetic corpus (`testing/synthetic_disputes.csv` and generator outputs) serves as a **unit/integration test suite** for deterministic rule coverage and regression testing. It must not be presented as an empirical research benchmark.

### Empirical Research Framework: Physical Observations

The frozen Phase 1 research study evaluates pre-delivery package verification under measurement uncertainty, permitted packaging changes, record inconsistencies, and observational indistinguishability. Empirical research data must strictly adhere to the physical observations schema defined in [`physical_observations_schema.md`](physical_observations_schema.md).

---

## 12. Security and Trust Model

Current implemented safeguards include:

- Offline local storage for pending telemetry.
- Encrypted Android preferences helper.
- HMAC packet signing scaffolding for BLE telemetry.
- Evidence provenance and timestamps.
- Human override audit records.
- Structured reasoning instead of opaque verdict text.
- Backend error handling and service health checks in the hardened stack.

Before production deployment, the following must be completed:

- Remove hardcoded demo secrets and coordinates.
- Use Android Keystore-backed key provisioning.
- Add authentication and authorization to all APIs.
- Restrict CORS and cleartext traffic.
- Validate BLE replay windows and signature freshness server-side.
- Encrypt evidence at rest and in transit.
- Add PII retention and deletion policies.
- Add tenant isolation and organization-level access controls.
- Validate all external webhook signatures.

---

## 13. Verification Status

The repository was verified on 2026-09-06 with:

| Verification | Result |
|---|---|
| Android Gradle debug build | Successful |
| Standalone backend Maven tests | 15 passed, 0 failed |
| Phase 1 Python tests | 8 passed, 0 failed |
| Phase 2/3 Spring Maven reactor | Successful; 15 tests passed in the tested module |

Some Phase 2 services contain no dedicated test sources, and full Docker/infrastructure runtime validation requires PostgreSQL, Redis, RabbitMQ, MinIO, and the configured environment.

---

## 14. Recommended Runtime Paths

### Compact mobile demonstration

1. Build the Android app with Gradle.
2. Start the root Spring backend from [backend](backend).
3. Run the Android app on a device or emulator.
4. Capture or enter a transcript.
5. Allow local fallback when Groq is unavailable.
6. Submit the locally queued telemetry packet.

### Enterprise platform demonstration

1. Start infrastructure from [phase-2/docker-compose.yml](TriNetra%20AI/phase-2/docker-compose.yml).
2. Start the Phase 2 claim and evidence services.
3. Start multimodal, fraud, verdict, and integration services.
4. Start the React dashboard.
5. Create a claim and upload evidence.
6. Follow asynchronous processing into the investigator queue.
7. Review reasoning and record an override when appropriate.

The compact path and enterprise path should be presented as separate deployment profiles until their contracts are formally unified.

---

## 15. Final Project Position

TriNetra AI is best understood as a layered evidence system:

- **Mobile layer:** captures observations at the physical event.
- **Evidence layer:** preserves raw files, measurements, timestamps, and provenance.
- **Analysis layer:** extracts bounded signals from text, images, documents, and behavior.
- **Reconciliation layer:** applies transparent rules across independent sources.
- **Investigation layer:** gives a human reviewer the context and authority to decide.
- **Research layer:** evaluates the approach on controlled and real-world-derived datasets.

The project's strongest contribution is the separation between evidence ingestion and high-stakes decision logic. Local and multimodal processing help convert messy observations into structured signals, while reconciliation and investigator review provide the explainability and accountability required for dispute resolution.
