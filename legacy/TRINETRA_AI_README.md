# TriNetra AI: Cross-Organizational Evidence Reconciliation & Multi-Modal Fraud Prevention Platform

[![Java 21](https://img.shields.io/badge/Java-21-orange.svg)](https://www.oracle.com/java/)
[![Spring Boot 3.2](https://img.shields.io/badge/Spring%20Boot-3.2-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)](https://www.typescriptlang.org/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-yellow.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.12-orange.svg)](https://www.rabbitmq.com/)
[![Redis](https://img.shields.io/badge/Redis-7-red.svg)](https://redis.io/)
[![Resilience4j](https://img.shields.io/badge/Resilience4j-2.2-blueviolet.svg)](https://resilience4j.readme.io/)

**TriNetra AI** (*"Three Eyes"*) is an enterprise fraud prevention and dispute resolution platform. It reconciles multi-source physical telemetry, visual artifacts, and digital logs across disparate e-commerce stakeholders (Merchants, Warehouses, Logistics Carriers, and Consumers) to eliminate return fraud, reduce false negatives, and guarantee auditable, non-hallucinatory dispute resolutions.

---

## 📚 Authoritative Research Master Documentation

For academic researchers, supervisors, and peer-reviewers, the complete project research corpus is maintained in:
👉 **[`TRINETRA_AI_MASTER_RESEARCH_DOCUMENTATION.md`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/TRINETRA_AI_MASTER_RESEARCH_DOCUMENTATION.md)**

### Research Artifacts & Data Ledger (`research/`)
* **Literature Matrix (244 papers with DOIs):** [`research/literature/literature_matrix.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/research/literature/literature_matrix.csv)
* **Real Consumer Complaint Corpus (1,050 cases):** [`research/complaints/complaint_evidence_matrix.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/research/complaints/complaint_evidence_matrix.csv)
* **Empirical Experiment Registry:** [`research/experiments/results_registry.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/research/experiments/results_registry.csv)
* **Figure & Visualization Inventory:** [`research/figures/figure_inventory.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/research/figures/figure_inventory.csv)
* **Claim Validation Ledger:** [`research/claims/claim_validation_ledger.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/research/claims/claim_validation_ledger.csv)

---

## 🚀 Key Highlights by Phase

| Phase | Title | Key Implementation & Scientific Milestones | Status |
|---|---|---|---|
| **Phase 1** | **Research MVP & Reconciler** | Deterministic conflict engine, entity resolution, canonical normalization, 1,000-case synthetic benchmark, **100% False Negative reduction** ($\chi^2 = 53.02, p = 3.30 \times 10^{-13}$). | ✅ **COMPLETE** |
| **Phase 2** | **Microservices & Multi-Modal** | 5 Spring Boot 3.2 services, OpenCV wear/EXIF vision pipeline, 4-signal fraud detector, and React 18 + Vite Investigator Dashboard. | ✅ **COMPLETE** |
| **Phase 3** | **Production Hardening & Scale** | Resilience4j Circuit Breakers, Exponential Retries, Flyway migrations (V1-V3), HikariCP pool tuning, Micrometer Prometheus metrics, and Locust load testing (p95 $< 100\text{ms}$). | ✅ **COMPLETE** |

---

## 🏗️ System Architecture

```
                                  ┌────────────────────────────────┐
                                  │   React Investigator Frontend  │
                                  │   (React 18 + TS + Vite / 5173)│
                                  └───────────────┬────────────────┘
                                                  │ HTTP / REST
┌───────────────────────────┐       ┌─────────────▼──────────────────┐
│   Third-Party Webhooks    ├──────►│      Claim Service             │ (Port 8080)
│  (Shipping, Payment, KYC) │       │ (Spring Boot 3.2 + JPA + Flyway)│
└─────────────┬─────────────┘       └─────────────┬──────────────────┘
              │                                   │
              │                     ┌─────────────▼──────────────────┐
              │                     │     Evidence Service           │ (Port 8081)
              │                     │ (Spring Boot 3.2 + MinIO SDK)  │
              │                     └─────────────┬──────────────────┘
              │                                   │
              │                     ┌─────────────▼──────────────────┐
              ├────────────────────►│      RabbitMQ Message Broker   │ (Port 5672)
              │                     │ (Exchanges, Queues, DLQ, DLX)  │
              │                     └─────────────┬──────────────────┘
              │                                   │
              │         ┌─────────────────────────┴─────────────────────────┐
              │         │                                                   │
              │ ┌───────▼──────────────────────┐            ┌───────────────▼────────────────┐
              │ │   Fraud Detection Engine     │            │      Verdict Generator         │
              │ │ (Spring Boot 3.2 / Port 8083)│            │ (Spring Boot 3.2 / Port 8084)  │
              │ └──────────────┬───────────────┘            └───────────────┬────────────────┘
              │                │                                            │
              ▼                ▼                                            ▼
       ┌───────────────────────────────────────────────────────────────────────────┐
       │   PostgreSQL 15 (Relational Data)  &  Redis 7 (Distributed Cache & TTL)   │
       └───────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure & Research Map

```
TriNetra AI/
├── TRINETRA_AI_MASTER_RESEARCH_DOCUMENTATION.md   # Authoritative master research source
├── research/                                      # Research CSV matrices, ledgers & figures
├── Public_Datasets/                               # 7 official Indian Govt NCH parliamentary datasets
├── xscrapper/                                     # 1,050 real consumer complaint dataset & mining tools
├── phase-1/                                       # Research MVP, reconciliation engine, baselines & evaluation
│   ├── README.md                                  # Phase 1 research documentation & execution guide
│   ├── generator/                                 # 1,000-case synthetic lifecycle generator (seed=42)
│   ├── engine/                                    # Deterministic reconciliation & conflict engine
│   └── evaluation/                                # Statistical evaluation suite & McNemar test
├── phase-2/                                       # Multi-service enterprise architecture & UI
│   ├── README.md                                  # Phase 2 architecture & port allocation guide
│   ├── spring-services/                           # 5 Spring Boot 3.2 microservices
│   ├── frontend-react/                            # React 18 + Vite Investigator Dashboard
│   └── services/multimodal_processor/             # Python FastAPI OpenCV & OCR processor
├── phase-3/                                       # Production hardening, migrations & load testing
│   ├── README.md                                  # Phase 3 hardening guide & SLA benchmarks
│   ├── PHASE_3_RESULTS.md                         # Official Phase 3 validation report
│   └── load_test/                                 # Locust load testing suite & Python runner
└── docker-compose.infra.yml                       # Backing infra (Postgres, Redis, RabbitMQ, MinIO)
```

---

## ⚡ Quick Start: Running Locally

### Step 1: Start Backing Infrastructure (Docker)
```powershell
cd "C:\Users\mitsu\Downloads\TriNetra AI\phase-2"
docker compose -f docker-compose.infra.yml up -d
```
*(Starts PostgreSQL on `5432`, Redis on `6379`, RabbitMQ on `5672`/`15672`, and MinIO on `9000`/`9001`)*.

### Step 2: Run Spring Boot Microservices
```powershell
cd "C:\Users\mitsu\Downloads\TriNetra AI\phase-2\spring-services\claim-service"
$env:PATH = "C:\Users\mitsu\Downloads\apache-maven-3.9.16-bin\apache-maven-3.9.16\bin;$env:PATH"
mvn spring-boot:run "-Dspring-boot.run.profiles=dev"
```

### Step 3: Run React Investigator Dashboard
```powershell
cd "C:\Users\mitsu\Downloads\TriNetra AI\phase-2\frontend-react"
npm.cmd run dev
```
Open **`http://localhost:5173`** in your browser.

### Step 4: Run Phase 3 Load Test Suite
```powershell
cd "C:\Users\mitsu\Downloads\TriNetra AI"
python phase-3/load_test/run_load_test.py --users 50 --spawn-rate 10 --duration 2m
```

---

## 📊 Experimental Results Summary

Evaluated across **1,000 synthetic lifecycle cases**:

| Metric | Baseline 1 (Identity Only) | Baseline 2 (Weight Only) | Baseline 3 (Timeline Only) | **TriNetra AI (Multi-Source)** | Target Threshold |
|---|---|---|---|---|---|
| **True Positives (TP)** | 30 | 40 | 15 | **95** | — |
| **False Positives (FP)** | 0 | 0 | 0 | **0** | — |
| **True Negatives (TN)** | 905 | 905 | 905 | **905** | — |
| **False Negatives (FN)** | 65 | 55 | 80 | **0** | — |
| **Precision** | 1.0000 | 1.0000 | 1.0000 | **1.0000** | $\ge 0.80$ ✅ |
| **Recall** | 0.3158 | 0.4211 | 0.1579 | **1.0000** | $\ge 0.75$ ✅ |
| **F1 Score** | 0.4800 | 0.5926 | 0.2727 | **1.0000** | $\ge 0.77$ ✅ |
| **FN Reduction vs Best Baseline** | 0.0% | 0.0% | 0.0% | **100.0%** | $> 15.0\%$ ✅ |

**Statistical Significance:** McNemar's $\chi^2 = 53.02, p = 3.3048 \times 10^{-13}$ ($p \ll 0.0001$).
