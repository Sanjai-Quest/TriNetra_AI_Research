# TriNetra-Link Architectural & Protocol Decisions

This document logs key binding decisions made during the execution of the research protocol.

---

## Decision D-01: Protocol Amendment v2.6.0 (Gate E-3 Withdrawal)
- **Date:** 2026-10-26
- **Context:** Protocol v2.5 conditioned physical study on Gate E-3 (4 independent human reviewers with Fleiss' $\kappa \ge 0.60$).
- **Decision:** Gate E-3 is formally withdrawn. The study is an **algorithm + dataset paper** comparing TriNetra-Link to 5 algorithmic baselines (B1–B5) across physical experiments E1 (attribution accuracy & abstention), E2 (perturbation robustness), and E3 (architectural ablations). Ground truth is derived deterministically from the physical staging log via code committed and hashed prior to capture.

## Decision D-02: Staging Sample Size and Stratification
- **Date:** 2026-10-26
- **Context:** Scenario cells distribution across the study cohort.
- **Decision:** Total physical cohort fixed at $N=120$ journeys across 8 scenario cells (`intact`: 30, `permitted_flyer`: 12, `forward_transit_damage`: 14, `doorstep_substitution`: 14, `customer_tamper`: 14, `reverse_transit_tamper`: 12, `degraded_evidence`: 12, `ambiguous_evidence`: 12). Shuffled presentation order with fixed seed. Partitioned into a 24-journey calibration set and a 96-journey test set (`split_manifest.json`).

## Decision D-03: Baseline B4 (LLM Judge) Groq Integration & Offline Determinism
- **Date:** 2026-10-26
- **Context:** Baseline B4 uses Groq `llama-3.3-70b-versatile` with temperature 0 and prompt `baselines/prompts/llm_judge_v1.txt`.
- **Decision:** When `GROQ_API_KEY` is present in the environment or `.env`, B4 executes live inference against Groq's API with 3 repeated runs. When `GROQ_API_KEY` is unset (such as in offline CI/testing environments), B4 executes a deterministic offline rule-based parser that faithfully mimics the prompt instructions without fabricated claims or network failure.

## Decision D-04: Baseline Scope (Text-Only vs Multimodal LLM)
- **Date:** 2026-10-26
- **Context:** Evaluation of potential multimodal extension to Baseline B4.
- **Decision:** As specified in protocol v2.6, Baseline B4 is evaluated as a structured text judge over the 4 checkpoint observation records. Multimodal visual reasoning is benchmarked natively through TriNetra-Link's visual reconciler and homography matching.
