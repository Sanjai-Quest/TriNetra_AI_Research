from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple
from trinetra_link.schema.models import Attribution

STAGES = ["ATTR_CONFIRMED_LEGITIMATE", "ATTR_STAGE(1)", "ATTR_STAGE(2)", "ATTR_STAGE(3)"]


def get_expected_state(stage: str, cp_index: int) -> str:
    """Expected physical state (INTACT or ANOM) at checkpoint k under stage hypothesis s."""
    if stage in ("ATTR_CONFIRMED_LEGITIMATE", "LEGITIMATE"):
        return "INTACT"
    if stage in ("ATTR_STAGE(1)", "STAGE(1)"):
        return "INTACT" if cp_index <= 1 else "ANOM"
    if stage in ("ATTR_STAGE(2)", "STAGE(2)"):
        return "INTACT" if cp_index <= 2 else "ANOM"
    if stage in ("ATTR_STAGE(3)", "STAGE(3)"):
        return "INTACT" if cp_index <= 3 else "ANOM"
    return "UNK"


def observation_likelihood(observed: str, expected: str, tpr: float = 0.95, fpr: float = 0.05) -> float:
    """Emission probability p(o_k | z_k(s))."""
    if observed == "UNK":
        return 0.50
    if expected == "ANOM":
        return tpr if observed == "ANOM" else (1.0 - tpr)
    else:  # expected == "INTACT"
        return (1.0 - fpr) if observed == "INTACT" else fpr


def attribute_bayes(
    journey_code: str,
    q_k: Dict[int, float],
    z_k: Dict[int, str],
    tau: float = 0.80,
    theta: float = 0.70,
    priors: Optional[Dict[str, float]] = None,
    tpr: float = 0.95,
    fpr: float = 0.05,
    k_max: int = 4,
) -> Attribution:
    """
    Bayesian chain-of-custody attribution with quality-exponent likelihoods:
        P(s | o) proportional to pi(s) * prod_{k=1}^K [ p(o_k | z_k(s)) ]^{q_k}

    Properties:
        - When q_k = 0, checkpoint k contributes factor 1.0 (completely uninformative).
        - Monotonic confidence in q_k.
        - Outputs argmax if posterior >= tau; otherwise abstains:
            * ABSTAIN_DEGRADED if an untrusted checkpoint (q_k < theta) lies in the interval.
            * ABSTAIN_INDISTINGUISHABLE otherwise.
    """
    if priors is None:
        priors = {s: 1.0 / len(STAGES) for s in STAGES}

    log_posteriors: Dict[str, float] = {}

    for stage in STAGES:
        log_prob = math.log(max(priors.get(stage, 1e-6), 1e-6))
        for k in range(1, k_max + 1):
            obs = z_k.get(k, "UNK")
            exp = get_expected_state(stage, k)
            lik = observation_likelihood(obs, exp, tpr=tpr, fpr=fpr)
            q = float(max(0.0, q_k.get(k, 0.0)))
            # Quality weighting: log(lik^q) = q * log(lik)
            log_prob += q * math.log(max(lik, 1e-9))
        log_posteriors[stage] = log_prob

    # Softmax normalization
    max_log = max(log_posteriors.values())
    unnorm_weights = {s: math.exp(lp - max_log) for s, lp in log_posteriors.items()}
    total_unnorm = sum(unnorm_weights.values())
    posterior = {s: round(unnorm_weights[s] / total_unnorm, 6) for s in STAGES}

    best_stage = max(posterior, key=lambda s: posterior[s])
    best_p = posterior[best_stage]

    trusted_set = [k for k in range(1, k_max + 1) if q_k.get(k, 0.0) >= theta]

    if best_p >= tau:
        # Confident resolution
        if best_stage in ("ATTR_CONFIRMED_LEGITIMATE", "LEGITIMATE"):
            interval = [1, k_max]
            label = "ATTR_CONFIRMED_LEGITIMATE"
            rationale = f"Bayesian attribution confirms unbroken transit with posterior {best_p:.4f} >= tau ({tau:.2f})."
        else:
            stage_idx = int(best_stage.split("(")[1][0])  # ATTR_STAGE(a) -> a
            interval = [stage_idx, stage_idx + 1]
            label = f"ATTR_STAGE({stage_idx})"
            rationale = f"Bayesian attribution isolates tamper to Stage {stage_idx} (CP{stage_idx}->CP{stage_idx+1}) with posterior {best_p:.4f} >= tau ({tau:.2f})."

        return Attribution(
            journey_code=journey_code,
            label=label,
            posterior=posterior,
            interval=interval,
            trusted_set=trusted_set,
            per_modality_evidence={"q_k": q_k, "z_k": z_k},
            rationale_text=rationale,
        )
    else:
        # Confidence below threshold tau -> determine abstention mode
        has_degraded = any(q_k.get(k, 0.0) < theta for k in range(1, k_max + 1))
        label = "ATTR_ABSTAIN_DEGRADED" if has_degraded else "ATTR_ABSTAIN_INDISTINGUISHABLE"
        rationale = (
            f"Posterior max ({best_p:.4f} for {best_stage}) below threshold tau ({tau:.2f}). "
            f"Classified as {label} due to {'degraded observation metadata' if has_degraded else 'inherent sensory ambiguity'}."
        )

        return Attribution(
            journey_code=journey_code,
            label=label,
            posterior=posterior,
            interval=None,
            trusted_set=trusted_set,
            per_modality_evidence={"q_k": q_k, "z_k": z_k},
            rationale_text=rationale,
        )
