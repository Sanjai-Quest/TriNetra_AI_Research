from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple
from trinetra_link.schema.models import Attribution


def attribute_interval_algorithm_1(
    journey_code: str,
    q_k: Dict[int, float],
    z_k: Dict[int, str],
    theta: float = 0.70,
    k_max: int = 4,
) -> Attribution:
    """
    Exact implementation of Algorithm 1: Causal Chain-of-Custody Attribution.

    Algorithm:
        T <- {k : q_k >= theta}
        if 1 not in T: return ABSTAIN_DEGRADED
        A <- {k in T : z_k = ANOM}
        if A = empty: return LEGITIMATE if K in T else ABSTAIN_DEGRADED
        b <- min A ; a <- max{k in T : k < b, z_k = INTACT}
        if exists k in (a, b) with q_k < theta: return ABSTAIN_DEGRADED
        if b = a + 1: return STAGE(a)
        return ABSTAIN_INDISTINGUISHABLE
    """
    # 1. Trusted set T
    T: Set[int] = {k for k in range(1, k_max + 1) if q_k.get(k, 0.0) >= theta}
    trusted_sorted: List[int] = sorted(list(T))

    # 2. Check baseline CP1 trust
    if 1 not in T:
        return Attribution(
            journey_code=journey_code,
            label="ATTR_ABSTAIN_DEGRADED",
            interval=None,
            trusted_set=trusted_sorted,
            per_modality_evidence={"q_k": q_k, "z_k": z_k},
            rationale_text="Baseline origin observation (CP1) quality q_1 < theta. Baseline ground truth cannot be established.",
        )

    # 3. Anomaly set A
    A: Set[int] = {k for k in T if z_k.get(k) == "ANOM"}

    # 4. No anomalies detected in trusted set
    if not A:
        if k_max in T:
            return Attribution(
                journey_code=journey_code,
                label="ATTR_CONFIRMED_LEGITIMATE",
                interval=[1, k_max],
                trusted_set=trusted_sorted,
                per_modality_evidence={"q_k": q_k, "z_k": z_k},
                rationale_text=f"All trusted checkpoints in 1..{k_max} show unbroken physical integrity through terminal destination CP{k_max}.",
            )
        else:
            return Attribution(
                journey_code=journey_code,
                label="ATTR_ABSTAIN_DEGRADED",
                interval=None,
                trusted_set=trusted_sorted,
                per_modality_evidence={"q_k": q_k, "z_k": z_k},
                rationale_text=f"No anomalies detected up to CP{max(T)}, but destination CP{k_max} observation was degraded/missing.",
            )

    # 5. First anomaly b and last intact a
    b = min(A)
    intact_prior = [k for k in T if k < b and z_k.get(k) == "INTACT"]
    a = max(intact_prior) if intact_prior else 0

    # 6. Check for uninformative/degraded intermediate checkpoints in (a, b)
    degraded_intermediate = [k for k in range(a + 1, b) if q_k.get(k, 0.0) < theta]
    if degraded_intermediate:
        return Attribution(
            journey_code=journey_code,
            label="ATTR_ABSTAIN_DEGRADED",
            interval=[a, b],
            trusted_set=trusted_sorted,
            per_modality_evidence={"q_k": q_k, "z_k": z_k, "degraded_in_interval": degraded_intermediate},
            rationale_text=f"Anomaly detected at CP{b} with prior intact CP{a}, but intermediate checkpoint(s) {degraded_intermediate} failed quality threshold (q < {theta:.2f}).",
        )

    # 7. Exact adjacent stage resolution
    if b == a + 1:
        stage_label = f"ATTR_STAGE({a})"
        return Attribution(
            journey_code=journey_code,
            label=stage_label,
            interval=[a, b],
            trusted_set=trusted_sorted,
            per_modality_evidence={"q_k": q_k, "z_k": z_k},
            rationale_text=f"Physical integrity confirmed intact at CP{a} and anomalous at CP{b}. Causal tamper uniquely isolated to Stage S{a} (transit interval CP{a}->CP{b}).",
        )

    # 8. Non-adjacent interval where checkpoints were trusted but state was ambiguous
    return Attribution(
        journey_code=journey_code,
        label="ATTR_ABSTAIN_INDISTINGUISHABLE",
        interval=[a, b],
        trusted_set=trusted_sorted,
        per_modality_evidence={"q_k": q_k, "z_k": z_k},
        rationale_text=f"Tamper occurred in multi-stage interval CP{a}->CP{b}, but intervening trusted checkpoints yielded UNK states, rendering stage attribution indistinguishable.",
    )
