# Systematic Literature Review Protocol: Evidence Continuity Across Open Box Delivery, Reverse Logistics, and E-Commerce Disputes in India

> **Protocol Version:** 1.0  
> **Date:** 2026-10-24  
> **Status:** Executed Research Protocol  
> **Focus Domain:** Indian e-commerce post-purchase verification, Open Box Delivery (OBD), reverse logistics, warehouse inspection, product substitution, and evidentiary dispute adjudication.  
> **Guiding Standard:** Adapted from PRISMA 2020 (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) and Fink's methodological framework for literature reviews.

---

## 1. Research Objectives and Scoping

### 1.1 Core Objective
Establish what published academic research, official government data, corporate operating policies, and adjudicated legal decisions already resolve regarding e-commerce returns, doorstep verification, and reverse logistics in India; identify author-acknowledged limitations and research agendas; and determine whether an empirically defensible research gap remains for TriNetra.

### 1.2 Candidate Research Question Under Evaluation
> *"How does evidence captured at Open Box Delivery and subsequent return/warehouse handovers affect the ability to distinguish product or fulfilment errors, logistics handling changes and unresolved disputes in Indian e-commerce?"*

### 1.3 Specific Review Questions (RQs)
- **RQ-L1 (Prior Art in Return Prediction & Fraud):** To what extent do existing statistical and machine learning models for return forecasting and refund fraud already solve the problem of identifying non-genuine returns, and what input features/labels do they rely on?
- **RQ-L2 (Doorstep & Handover Verification Mechanisms):** How have doorstep inspection policies (specifically Open Box Delivery in India) and handover documentation protocols been modeled or evaluated in academic, industrial, and legal literature?
- **RQ-L3 (Reverse Logistics Anomaly Detection & Warehouse Grading):** What methodologies exist for inspecting returned goods at fulfillment centers, how do they handle physical condition grading, and do they track custody continuity backwards to the point of origin?
- **RQ-L4 (Indian Operational, Legal, and Consumer Context):** What are the documented institutional, behavioral, and legal constraints governing e-commerce returns in India (including National Consumer Helpline data, Consumer Protection Rules, and Consumer Commission case law)?
- **RQ-L5 (Methodological Defensibility):** Does any existing study evaluate a multi-stage evidence chain (combining doorstep delivery, return pickup, and warehouse receiving) under observation uncertainty and abstention, or does this represent an unaddressed research gap?

---

## 2. Search Strategy and Information Sources

### 2.1 Academic Databases and Repositories
Searches were conducted across the following electronic databases, citation indices, and preprint repositories:
1. **Scopus / Elsevier ScienceDirect** (Operations Management, Supply Chain, Decision Sciences)
2. **Web of Science / Clarivate** (Management, Transportation, Industrial Engineering)
3. **IEEE Xplore Digital Library** (Logistics Informatics, IoT Telematics, Computer Vision)
4. **ACM Digital Library** (Information Systems, Applied Computing, E-Commerce Architectures)
5. **SpringerLink / Emerald Insight** (Annals of Operations Research, IJPDLM, Management Review Quarterly)
6. **SSRN (Social Science Research Network)** (Economics, Operations Research Working Papers)
7. **Indian Academic Journals & Portals** (Indian Journal of Marketing, e-Courts India, LiveLaw, Casemine)

### 2.2 Institutional, Policy, and Official Sources
To anchor the empirical context in India:
1. **Department of Consumer Affairs, Government of India / Press Information Bureau (PIB)** (National Consumer Helpline grievance disclosures, Consumer Protection (E-Commerce) Rules 2020 and 2026 Amendments)
2. **E-Commerce Platform Operating Terms** (Flipkart Open Box Delivery Terms & Conditions, Amazon India Delivery & Return Policies)
3. **District Consumer Disputes Redressal Commission (DCDRC) Adjudications** (Published orders from Central Mumbai, Adilabad, Kurnool, Rangareddy Commissions via official court repositories and legal reporter services)

### 2.3 Search Strings and Boolean Construction
Search strings were organized into 7 thematic blocks:

| Block | Thematic Focus | Canonical Query String |
|:---:|---|---|
| **A** | Return Forecasting & Behavior | `("e-commerce" OR "online retail") AND ("return forecasting" OR "return prediction" OR "product return behavior") AND ("India" OR "consumer behavior")` |
| **B** | Return Fraud & Opportunism | `("return fraud" OR "fraudulent returns" OR "wardrobing" OR "refund fraud" OR "deshopping") AND ("e-commerce" OR "retail")` |
| **C** | Open Box Delivery & Doorstep Handovers | `("Open Box Delivery" OR "doorstep inspection" OR "delivery verification") AND ("India" OR "Flipkart" OR "Amazon" OR "OTP")` |
| **D** | Reverse Logistics & Anomaly Detection | `("reverse logistics" OR "returns management") AND ("anomaly detection" OR "automated grading" OR "inspection") AND ("e-commerce")` |
| **E** | Product Substitution & Mis-shipment | `("product substitution" OR "wrong item" OR "empty box" OR "item swap" OR "tampering") AND ("e-commerce" OR "logistics")` |
| **F** | Chain of Custody & Evidence Provenance | `("chain of custody" OR "evidence provenance" OR "handover documentation" OR "tamper-evident") AND ("last-mile" OR "reverse logistics")` |
| **G** | Indian Legal & Grievance Context | `("Consumer Protection Act" OR "Consumer Commission" OR "deficiency in service") AND ("e-commerce" OR "wrong product" OR "unboxing video") AND ("India")` |

---

## 3. Eligibility Criteria (Inclusion and Exclusion)

### 3.1 Inclusion Criteria (IC)
- **IC-1 (Domain):** Peer-reviewed journal articles, conference proceedings, academic working papers, official government reports, statutory rules, marketplace policies, and adjudicated court orders directly addressing e-commerce returns, return fraud, doorstep inspection, or reverse logistics.
- **IC-2 (Empirical Context):** Global papers addressing core methodological techniques (ML, analytics, game theory, anomaly detection) AND India-specific studies establishing operational, behavioral, or legal realities.
- **IC-3 (Traceability):** Must have an authentic Digital Object Identifier (DOI), permanent institutional handle, official government URL, or verifiable case citation.
- **IC-4 (Date Range):** Foundational literature from 2005 onwards; contemporary focus spanning 2020 to 2026.

### 3.2 Exclusion Criteria (EC)
- **EC-1 (Unverified Records):** Blog posts, unverified news op-eds, anonymous forum complaints, or marketing whitepapers lacking empirical methodology.
- **EC-2 (Generic Fraud):** General payment/credit-card fraud detection studies that do not address physical item identity, physical condition, or logistics custody.
- **EC-3 (Uncalibrated Scraping):** Studies using unverified social media complaints as ground-truth fraud labels (specifically excluding methods related to TriNetra's quarantined complaint corpus).
- **EC-4 (Pure Forward Logistics):** Forward routing and vehicle fleet optimization papers that contain no reverse logistics, return inspection, or dispute modeling.

---

## 4. Screening and Data Extraction Protocol

### 4.1 Screening Stages
1. **Title & Abstract Screening:** Records identified through electronic search were screened against IC/EC.
2. **Accessibility Verification:** Records were strictly categorized as:
   - `FULL_TEXT_REVIEWED`: Full academic text retrieved, read, and verified.
   - `ABSTRACT_ONLY_REVIEWED`: Only abstract, index metadata, and publisher summary accessed (labeled explicitly).
   - `OFFICIAL_POLICY_REVIEWED`: Primary legal text or corporate operating terms inspected directly.
   - `ADJUDICATED_CASE_REVIEWED`: Primary or accredited secondary legal reporter text inspected.
   *Rule:* No abstract-only record is permitted to be cited as having undergone full-text review.
3. **Data Extraction Schema:**
   Every included record was extracted into a standardized schema capturing:
   - Citation & Year
   - Geographic Scope & Author Affiliation
   - Evidence Type & Dataset Sample Size
   - Research Objective
   - Ground-Truth Definition
   - Methodology & Baselines
   - Performance Metrics
   - Author-Acknowledged Explicit Limitations
   - Author-Recommended Future Work
   - Direct Implication for TriNetra

---

## 5. Synthesis and Research Gap Evaluation Framework

Extracted papers are synthesized to test whether existing literature resolves the candidate research question across 5 dimensions:
1. **Multi-Source Cross-Stage Linkage:** Does the literature link pre-delivery/doorstep inspection, reverse carrier pickup, and warehouse receiving into a unified evidentiary record?
2. **Physical Observation vs. Customer Allegation:** Does the literature rely on subjective customer claims/surveys or calibrated physical measurements?
3. **Separation of Fulfilment Error, Transit Damage, and Fraud:** Can existing systems differentiate between merchant shipping mistakes, courier mishandling, and intentional customer substitution?
4. **Uncertainty & Explicit Abstention:** Does the model or policy abstain (`INDISTINGUISHABLE` / `INSUFFICIENT_EVIDENCE`) when physical signals fall within instrument measurement noise?
5. **Operational Viability in India:** Can the proposed framework function within Indian high-velocity sorting terminals, doorstep COD constraints, and DCDRC legal standards?
