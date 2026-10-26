# TriNetra AI: Phase 3 — Production Hardening, Observability & Load Testing

[![Spring Boot 3.2](https://img.shields.io/badge/Spring%20Boot-3.2-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![Resilience4j](https://img.shields.io/badge/Resilience4j-2.2-blueviolet.svg)](https://resilience4j.readme.io/)
[![Flyway](https://img.shields.io/badge/Flyway-10.10-red.svg)](https://flywaydb.org/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Micrometer-orange.svg)](https://micrometer.io/)
[![Locust](https://img.shields.io/badge/Locust-2.46-green.svg)](https://locust.io/)

Phase 3 transitions TriNetra AI from a research prototype into an **enterprise-grade, production-hardened microservices platform**. It introduces fault-tolerant circuit breakers, exponential backoff retries, database migration version control, connection pool tuning, structured JSON logging, distributed Prometheus metrics, and concurrent load benchmarking.

---

## 📑 Research & Academic Cross-References

For research paper construction, the empirical benchmarks and architectural decisions from Phase 3 are formally documented in:
* **Master Research Document:** [`TRINETRA_AI_MASTER_RESEARCH_DOCUMENTATION.md`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/TRINETRA_AI_MASTER_RESEARCH_DOCUMENTATION.md)
* **Official Phase 3 Validation Report:** [`phase-3/PHASE_3_RESULTS.md`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-3/PHASE_3_RESULTS.md)
* **Results Registry:** [`research/experiments/results_registry.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/research/experiments/results_registry.csv)
* **Load Test Latency & SLA Data:** [`phase-3/load_test/results/`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-3/load_test/results/)

---

## 🛠️ Key Production Hardening Components

### 1. Resilience4j Fault Isolation (`@CircuitBreaker` & `@Retry`)
Configured across all I/O pathways (PostgreSQL JPA, RabbitMQ publishing, Redis caching, MinIO storage):
- **Sliding Window:** 10 calls with 30–50% failure rate threshold before opening.
- **Wait Duration in OPEN State:** 30 seconds (15s for Redis for fast recovery).
- **Exponential Backoff Retry:** 3 attempts with initial delay of 100ms and 2.0x multiplier.
- **Graceful Fallbacks:** Guaranteed DB persistence even during transient message broker downtime.

### 2. Flyway Database Schema Versioning
Replaced unsafe `ddl-auto: update` with strict `ddl-auto: validate` and version-controlled SQL migrations:
- **`V1__initial_schema.sql`:** Baseline Phase 2 entities (Claims, Evidence, Artifacts, Fraud Signals, Verdicts).
- **`V2__add_audit_log.sql`:** Unified system audit logs, circuit breaker state transitions, and Dead Letter Queue tracking.
- **`V3__health_monitoring_tables.sql`:** Service health snapshots, HikariCP connection pool telemetry, and SLA performance baselines.

### 3. HikariCP Connection Pool Optimization
- Max Pool Size: **20 connections**
- Min Idle Connections: **5 connections**
- Connection Timeout: **30,000 ms**
- Leak Detection Threshold: **60,000 ms**

### 4. Observability, Metrics & Structured Logging
- **Micrometer + Prometheus:** Real-time business counters (`trinetra.claims.ingested`, `trinetra.claims.overrides.applied`) and latency percentile summaries (`trinetra.claims.processing.duration`).
- **Logstash JSON Encoder:** Structured logs with `traceId` and `spanId` injection across all 5 services for ELK Stack ingestion.
- **Actuator Health Endpoints:** Detailed component health checks exposed at `/actuator/health`, `/actuator/prometheus`, and `/actuator/circuitbreakers`.

### 5. Centralized Global Exception Handlers
- **RFC 7807 Compliant Responses:** Deterministic mapping of domain exceptions to HTTP status codes (`404 ClaimNotFoundException`, `409 ClaimConflictException`, `400 ValidationError`, `503 CircuitOpenException`, `504 TimeoutException`).
- **Zero Information Leakage:** Stack traces and internal server details are never leaked to clients.

---

## 📈 Empirical Performance & SLA Benchmark Results

Executed via Locust load testing suite (`phase-3/load_test/run_load_test.py`):

| API Endpoint / Action | Measured p95 Latency | Configured SLA Target | Failure Rate | Status |
|---|---|---|---|---|
| `POST /api/v2/claims` (Create Claim) | **70.0 ms** | < 2000 ms | 0.00% | ✅ **PASS** |
| `GET /api/v2/claims/search` (Search Queue) | **50.0 ms** | < 1000 ms | 0.00% | ✅ **PASS** |
| `GET /api/v2/claims/{id}` (Claim Detail) | **81.0 ms** | < 1500 ms | 0.00% | ✅ **PASS** |
| `GET /api/v2/claims/health` (Health Check) | **37.0 ms** | < 5000 ms | 0.00% | ✅ **PASS** |
| **Aggregated Test Failure Rate** | **0.00%** | **< 1.00%** | — | ✅ **PASS** |

---

## ⚡ Execution Instructions

### 1. Compile and Execute Unit Tests
```powershell
cd "C:\Users\mitsu\Downloads\TriNetra AI\phase-2\spring-services"
$env:PATH = "C:\Users\mitsu\Downloads\apache-maven-3.9.16-bin\apache-maven-3.9.16\bin;$env:PATH"
mvn test
```

### 2. Run the Automated Load Test Suite
```powershell
cd "C:\Users\mitsu\Downloads\TriNetra AI"
python phase-3/load_test/run_load_test.py --users 50 --spawn-rate 10 --duration 2m
```
*(Generates an interactive HTML report and CSV metrics in `phase-3/load_test/results/`)*.
