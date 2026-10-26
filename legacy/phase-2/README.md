# TriNetra AI: Phase 2 — Multi-Modal Processing & Microservices Architecture

[![Java 21](https://img.shields.io/badge/Java-21-orange.svg)](https://www.oracle.com/java/)
[![Spring Boot 3.2](https://img.shields.io/badge/Spring%20Boot-3.2-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)](https://www.typescriptlang.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Python-brightgreen.svg)](https://opencv.org/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.12-orange.svg)](https://www.rabbitmq.com/)

Phase 2 scales the Phase 1 evidence reconciliation foundation into a **distributed, event-driven multi-service platform**. It introduces Spring Boot 3.2 microservices, a lightweight computer vision pipeline for return garment/receipt inspection, an advanced 4-signal fraud detection engine, and a modern React 18 investigator dashboard.

---

## 📑 Research Paper Cross-References & Tags

For drafting the research paper, the Phase 2 system architecture, multi-modal processing formulas, and database schemas are tagged and indexed in:
* **Master Research Document:** [`TRINETRA_AI_MASTER_RESEARCH_DOCUMENTATION.md`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/TRINETRA_AI_MASTER_RESEARCH_DOCUMENTATION.md) (Sections 12, 13, 14, 16, 17)
* **Real Consumer Complaint Corpus (1,050 cases):** [`xscrapper/trinetra_real_complaints_expanded.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/xscrapper/trinetra_real_complaints_expanded.csv)
* **Microservices Parent POM:** [`phase-2/spring-services/pom.xml`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-2/spring-services/pom.xml)
* **Database Schema Extensions:** [`phase-2/schema/schema_extensions.sql`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-2/schema/schema_extensions.sql)
* **React Investigator Dashboard:** [`phase-2/frontend-react/`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/phase-2/frontend-react/)
* **System Architecture Diagram:** [`research/figures/figure_inventory.csv`](file:///c:/Users/mitsu/Downloads/TriNetra%20AI/research/figures/figure_inventory.csv) (FIG-01)

---

## 🏗️ Microservices & Port Allocation

```
                                  ┌────────────────────────────────┐
                                  │   React Investigator Frontend  │
                                  │   (React 18 + TS + Vite / 5173)│
                                  └───────────────┬────────────────┘
                                                  │ HTTP / REST
┌───────────────────────────┐       ┌─────────────▼──────────────────┐
│   Third-Party Webhooks    ├──────►│      Claim Service             │ (Port 8080)
│  (Shipping, Payment, KYC) │       │ (Spring Boot 3.2 + JPA + REST) │
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

| Service | Port | Technology | Key Responsibility |
|---|---|---|---|
| **Claim Service** | 8080 | Spring Boot 3.2 + JPA | Claim ingestion, lifecycle management, investigator overrides |
| **Evidence Service** | 8081 | Spring Boot 3.2 + MinIO | S3-compatible multi-modal file storage & metadata extraction |
| **Multi-Modal Processor** | 8082 | Python FastAPI + OpenCV | Computer vision: wear detection, color consistency, EXIF, OCR |
| **Fraud Detection Engine**| 8083 | Spring Boot 3.2 + Redis | 4-signal fraud detection (serial fraud, wardrobing, velocity) |
| **Verdict Generator** | 8084 | Spring Boot 3.2 + Redis | Weighted factor risk scoring & 100% explainable template reasoning |
| **Integration Service** | 8085 | Spring Boot 3.2 + AMQP | Carrier delivery webhooks, payment status, DLQ management |
| **Investigator Dashboard**| 5173 | React 18 + TS + Tailwind | Triage queue, risk meters, and human-in-the-loop override UI |

---

## ⚡ Quick Start: Running Locally

### 1. Start Backing Infrastructure (Docker)
```powershell
cd "C:\Users\mitsu\Downloads\TriNetra AI\phase-2"
docker compose -f docker-compose.infra.yml up -d
```

### 2. Start Claim Service (Port 8080)
```powershell
cd "C:\Users\mitsu\Downloads\TriNetra AI\phase-2\spring-services\claim-service"
$env:PATH = "C:\Users\mitsu\Downloads\apache-maven-3.9.16-bin\apache-maven-3.9.16\bin;$env:PATH"
mvn spring-boot:run "-Dspring-boot.run.profiles=dev"
```

### 3. Start React Investigator Dashboard (Port 5173)
```powershell
cd "C:\Users\mitsu\Downloads\TriNetra AI\phase-2\frontend-react"
npm.cmd run dev
```
Open **`http://localhost:5173`** to access the live triage queue.
