# Search Reconciliation Report

> **Document Type:** Stage 2B Evidence Audit — Search Reconciliation  
> **Date:** 2026-10-24  
> **Reviewer Role:** Independent Research-Methodology Reviewer  
> **Input Files:** `literature_search_log.csv`, `closest_work_matrix.csv`, `literature_search_protocol.md`  
> **Rule:** Original files preserved. This is a corrective overlay, not a replacement.

---

## 1. Numerical Reconciliation

### 1.1 Search Log Totals (Summed from 8 Queries)

| Metric | Reported Value | Recalculated Value | Status |
|---|:---:|:---:|:---:|
| Total Retrieved | Not reported | **245** | COMPUTED |
| Total Screened | Not reported | **114** | COMPUTED |
| Total Excluded at Screening | Not reported | **90** | COMPUTED |
| Total Included (per-query sum) | Not reported | **24** | COMPUTED |
| Duplicates Removed | Not reported | **0 (unreported)** | **MISSING** |

> [!WARNING]
> The search log reports no aggregate totals and no deduplication stage. The per-query included counts sum to 24, but the closest work matrix contains only 16 entries. This 8-record discrepancy is unexplained.

### 1.2 Per-Query Breakdown

| Query | Block | Retrieved | Screened | Included | Not Screened | Excluded |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Q01 | A: Return Forecasting | 42 | 18 | 3 | 24 | 15 |
| Q02 | B: Return Fraud | 38 | 15 | 4 | 23 | 11 |
| Q03 | C: Open Box Delivery | 19 | 12 | 3 | 7 | 9 |
| Q04 | D: Reverse Logistics | 51 | 20 | 3 | 31 | 17 |
| Q05 | E: Product Substitution | 34 | 14 | 3 | 20 | 11 |
| Q06 | F: Chain of Custody | 29 | 11 | 2 | 18 | 9 |
| Q07 | G: Indian Jurisprudence | 24 | 16 | 4 | 8 | 12 |
| Q08 | G: Official Grievance Data | 8 | 8 | 2 | 0 | 6 |
| **TOTAL** | | **245** | **114** | **24** | **131** | **90** |

### 1.3 The 24 → 16 Discrepancy

**Matrix contains 16 entries.** The 8-entry gap admits three possible explanations:

1. **Hypothesis A (Deduplication):** Some records appeared in multiple block queries and were deduplicated when populating the matrix, but the per-query "included" counts reflect pre-deduplication totals. **Plausible:** Bhattacharya (2026) could appear in both Block B and Block G; Kar et al. (2024) could appear in both Block A and Block C. However, this requires at least 8 cross-block duplicates, which is implausible given the domain specificity of the queries.

2. **Hypothesis B (Full-Text Exclusion):** 8 records passed title/abstract screening ("included" at that stage) but were subsequently excluded after full-text review. **Most likely.** However, the search log has no `excluded_at_full_text` column, no `exclusion_reason` field, and no PRISMA flow diagram documenting this stage.

3. **Hypothesis C (Estimation):** The per-query included counts were estimated rather than precisely tracked. **Cannot be ruled out** given that all 8 queries were executed on the same date.

**Required correction:** The search log must add a screening stage column (e.g., `records_excluded_at_full_text`) or revise per-query included counts to reconcile with the 16 matrix entries. The corrected `screening_ledger.csv` documents this.

---

## 2. Missing PRISMA Flow

The protocol claims adaptation from PRISMA 2020 but provides no PRISMA flow diagram. A compliant flow must report:

```
Records identified through database searching:  (unknown — see §3)
Records identified through other sources:        (unknown)
                         │
                         ▼
Records after duplicates removed:                (unknown — 0 reported)
                         │
                         ▼
Records screened (title/abstract):               114
Records excluded at screening:                   90
                         │
                         ▼
Full-text articles assessed for eligibility:      24
Full-text articles excluded (with reasons):       8 (unaccounted)
                         │
                         ▼
Studies included in synthesis:                    16
  - Academic papers:                              10
  - Corporate/government policy documents:        2
  - Adjudicated legal decisions:                  4
```

> [!IMPORTANT]
> This flow cannot be completed because the "records identified" total (245) conflates actual database searches, web searches, legal portal browsing, and government press release retrieval under a single count. See §3.

---

## 3. Search Type Classification

### 3.1 The Problem

The search log lists source databases that range from curated academic indices (Scopus, IEEE Xplore) to general web search (Google Scholar) to government press archives (PIB). A PRISMA-compliant protocol must distinguish structured database searches from supplementary sources.

### 3.2 Reclassification

| Query | Claimed Source | Actual Search Type | Verification Status |
|:---:|---|---|:---:|
| Q01 | Scopus / Web of Science | **Academic database search** | **UNVERIFIED** — no search export, saved search URL, or screenshot attached |
| Q02 | Elsevier / SpringerLink | **Publisher portal search** — Elsevier ScienceDirect and SpringerLink are publisher portals, not independent curated indices | **UNVERIFIED** |
| Q03 | Indian Academic Portals / Google Scholar | **Web search engine** — Google Scholar is not a curated database; it indexes heterogeneous sources with variable quality control | **UNVERIFIED** |
| Q04 | Emerald / Annals of Operations Research | **Publisher portal search** — Emerald Insight is a publisher platform; Annals of Operations Research is a single journal | **UNVERIFIED** |
| Q05 | IEEE Xplore / ACM Digital Library | **Academic database search** | **UNVERIFIED** |
| Q06 | IEEE Xplore / SpringerLink | **Mixed: database + publisher** | **UNVERIFIED** |
| Q07 | Indian Legal Portals (Casemine/LiveLaw/eCourts) | **Legal case repository / legal news aggregator** — Casemine is a commercial case search engine; LiveLaw is a legal news portal; eCourts is the official Indian judicial repository | **PARTIALLY VERIFIED** — URLs resolve for LiveLaw articles |
| Q08 | PIB / Ministry of Consumer Affairs | **Government press release archive** | **PARTIALLY VERIFIED** — PIB URL resolves |

### 3.3 Critical Observation

**No evidence confirms that Scopus, Web of Science, IEEE Xplore, or ACM Digital Library were actually searched.** The claimed source databases for Q01, Q02, Q04, Q05, and Q06 require institutional subscriptions. No institutional affiliation, subscription proof, or exported search history is documented.

This does not prove the searches were fabricated. It means they are **not reproducible and not independently verifiable** — a requirement for any systematic review claiming PRISMA adaptation.

**Honest reclassification:** These should be described as "structured searches across academic publisher platforms and citation indices" with the caveat that reproducibility documentation is incomplete. The strongest verifiable claim is: "literature was identified through a combination of publisher portal searches, Google Scholar, legal case databases, and government press archives."

---

## 4. Query String Discrepancies

The protocol (Section 2.3) and the search log contain **different query strings** for the same thematic blocks:

| Block | Protocol Query (Section 2.3) | Search Log Query (CSV) | Discrepancy |
|:---:|---|---|---|
| A | Includes `AND ("India" OR "consumer behavior")` | Does **not** include India/consumer behavior filter | Protocol is more restrictive |
| B | Includes `"deshopping"` | Does **not** include deshopping | Minor keyword omission |
| C | Includes `"delivery verification"` | Does **not** include delivery verification | Minor keyword omission |
| D | Includes `AND ("e-commerce")` | Does **not** include e-commerce filter | Protocol is more restrictive |
| E | Includes `"empty box"` and `"tampering"` | Does **not** include empty box or tampering | Significant keyword omission |
| F | Includes `"tamper-evident"` | Does **not** include tamper-evident | Minor keyword omission |
| G | Includes `AND ("India")` | Does **not** include India filter | Protocol is more restrictive |

> [!WARNING]
> When the documented protocol query and the actually-executed query differ, neither is reproducible. The corrected protocol must use a single canonical query string per block.

---

## 5. Temporal Concerns

All 8 queries show `date_executed = 2026-10-24`. This is consistent with a single-session batch execution rather than iterative search-screen-refine cycles. This is acceptable for a rapid scoping review but should be honestly characterized as such, rather than implying a multi-session systematic search process.

---

## 6. Summary of Required Corrections

| Issue | Severity | Correction |
|---|:---:|---|
| 24→16 discrepancy unexplained | Critical | Add full-text exclusion accounting or revise per-query counts |
| No PRISMA flow diagram | Critical | Add flow diagram with all stages |
| No deduplication stage | High | Add deduplication accounting |
| Database access unverified | High | Reclassify as "unverified" or provide search exports |
| Query strings inconsistent between protocol and log | Moderate | Canonicalize to single query string per block |
| Same-day execution not characterized | Low | Label as "single-session structured scoping search" |
| Search log lacks aggregate totals | Low | Add summary row |
