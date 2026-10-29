from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple
from trinetra_link.schema.models import Attribution

STAGES = [
    "ATTR_CONFIRMED_LEGITIMATE",
    "ATTR_STAGE_FORWARD_TRANSIT",
    "ATTR_STAGE_CONSUMER_CUSTODY",
    "ATTR_STAGE_REVERSE_TRANSIT",
]


def get_expected_state(stage: str, cp_index: int) -> str:
    """Expected physical state (INTACT or ANOM) at checkpoint k under stage hypothesis s."""
    if stage in ("ATTR_CONFIRMED_LEGITIMATE", "LEGITIMATE"):
        return "INTACT"
    if stage in ("ATTR_STAGE_FORWARD_TRANSIT", "ATTR_STAGE(1)", "STAGE(1)"):
        return "INTACT" if cp_index <= 1 else "ANOM"
    if stage in ("ATTR_STAGE_CONSUMER_CUSTODY", "ATTR_STAGE(2)", "STAGE(2)"):
        return "INTACT" if cp_index <= 2 else "ANOM"
    if stage in ("ATTR_STAGE_REVERSE_TRANSIT", "ATTR_STAGE(3)", "STAGE(3)"):
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
    modality_evidence: Optional[Dict[int, Dict[str, Tuple[str, float]]]] = None,
) -> Attribution:
    """
    Bayesian chain-of-custody attribution with per-modality quality-exponent likelihoods:
        P(s | o) proportional to pi(s) * prod_{k=1}^K prod_{m} [ p(o_{k,m} | z_k(s)) ]^{q_{k,m}}

    Properties:
        - When q_{k,m} = 0, modality m contributes factor 1.0 (uninformative).
        - Monotonic confidence in per-modality trust factors.
        - Bad weight reading does not degrade photo or seal modalities.
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
            exp = get_expected_state(stage, k)
            if modality_evidence and k in modality_evidence:
                for mod_name, (obs, q_mod) in modality_evidence[k].items():
                    if obs == "UNK" or q_mod < 0.05:
                        continue
                    lik = observation_likelihood(obs, exp, tpr=tpr, fpr=fpr)
                    log_prob += float(max(0.0, q_mod)) * math.log(max(lik, 1e-9))
            else:
                obs = z_k.get(k, "UNK")
                lik = observation_likelihood(obs, exp, tpr=tpr, fpr=fpr)
                q = float(max(0.0, q_k.get(k, 0.0)))
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

    stage_intervals = {
        "ATTR_CONFIRMED_LEGITIMATE": [1, k_max],
        "ATTR_STAGE_FORWARD_TRANSIT": [1, 2],
        "ATTR_STAGE_CONSUMER_CUSTODY": [2, 3],
        "ATTR_STAGE_REVERSE_TRANSIT": [3, 4],
    }

    if best_p >= tau:
        # Confident resolution
        interval = stage_intervals.get(best_stage, [1, k_max])
        # A checkpoint inside (a,b] with untrusted quality -> ABSTAIN_DEGRADED
        if best_stage != "ATTR_CONFIRMED_LEGITIMATE" and any(q_k.get(k, 0.0) < theta for k in (interval[0], interval[1])):
            label = "ATTR_ABSTAIN_DEGRADED"
            interval = None
            rationale = (
                f"Candidate Bayesian stage {best_stage} bounding checkpoint quality < theta ({theta:.2f}). "
                f"Degraded causal attribution."
            )
        else:
            label = best_stage
            rationale = f"Bayesian attribution isolates {best_stage} with posterior {best_p:.4f} >= tau ({tau:.2f})."

        return Attribution(
            journey_code=journey_code,
            label=label,
            posterior=posterior,
            interval=interval,
            trusted_set=trusted_set,
            per_modality_evidence={"q_k": q_k, "z_k": z_k, "modality_evidence": modality_evidence},
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
