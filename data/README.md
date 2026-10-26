# TriNetra Data Storage and Layout

This directory houses research datasets, public baselines, and local raw capture artifacts for the TriNetra-Link research project.

---

## Directory Layout

```
data/
├── public/                 # Public benchmark and reference datasets
│   └── nch/                # Official Rajya Sabha / National Consumer Helpline tables (documented in SOURCES.md)
│
├── derived/                # Local derived data (scale calibrations, fitted noise parameters; gitignored)
├── artifacts/              # Local raw image artifacts organized by journey and checkpoint (gitignored)
│   └── <journey_id>/
│       └── <checkpoint>/
│           └── <image_files> (SHA-256 recorded at ingest)
│
└── restricted/             # Embargoed evaluation ledgers and unblinded keys (STRICTLY EMBARGOED; gitignored)
```

---

## Data Governance & Integrity Rules

1. **Strict Decoupling of Ground Truth:** Empirical sensor observations must never contain or receive ground-truth labels.
2. **Provenance Mandatory:** All external or harvested public datasets must include a `SOURCES.md` or manifest documenting origin, date, license, and question numbers.
3. **No Synthetic Masquerading:** Synthetic unit test fixtures must reside exclusively under `tests/fixtures/synthetic/` with explicit `"synthetic": true` tags.
4. **Append-Only Immutability:** Checkpoint sensor telemetry and capture logs are append-only.
