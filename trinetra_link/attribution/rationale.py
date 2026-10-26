from __future__ import annotations

from typing import Any, Dict, List, Optional


def generate_attribution_rationale(
    journey_code: str,
    label: str,
    interval: Optional[List[int]],
    trusted_set: List[int],
    per_modality_evidence: Dict[str, Any],
    decision: Optional[str] = None,
) -> str:
    """Generate detailed, structured human-readable rationale text."""
    lines: List[str] = []
    lines.append(f"Attribution Rationale for Journey {journey_code}:")
    lines.append(f"  Final Attribution: {label}")
    if interval:
        lines.append(f"  Isolated Interval: CP{interval[0]} -> CP{interval[1]}")
    lines.append(f"  Trusted Checkpoints (q >= theta): {sorted(trusted_set)}")

    if decision:
        lines.append(f"  Normative Operational Decision: {decision}")

    lines.append("  Evidence Breakdown:")
    q_k = per_modality_evidence.get("q_k", {})
    z_k = per_modality_evidence.get("z_k", {})

    for k in sorted(list(set(list(q_k.keys()) + list(z_k.keys())))):
        q_val = q_k.get(k, "N/A")
        z_val = z_k.get(k, "N/A")
        q_str = f"{q_val:.3f}" if isinstance(q_val, (int, float)) else str(q_val)
        lines.append(f"    - CP{k}: State={z_val}, QualityScore={q_str}")

    if "degraded_in_interval" in per_modality_evidence:
        deg = per_modality_evidence["degraded_in_interval"]
        lines.append(f"  Degraded Intervening Checkpoints: {deg} (induced ABSTAIN_DEGRADED)")

    return "\n".join(lines)
