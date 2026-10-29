from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def derive_ground_truth(
    staging_row: Dict[str, Any],
    capture_quality_passed: bool = True,
    mask: str = "full",
) -> Tuple[str, str, Optional[List[int]]]:
    """
    Deterministic Ground-Truth Derivation Rule (Amendment v2.6 §4.3).
    Evaluates physical staging log parameters and capture quality check to produce:
        (omega_star, expected_label, ground_truth_interval)

    Deterministic Mapping Table:
        - No manipulation, no degradation -> DET, ATTR_CONFIRMED_LEGITIMATE
        - Manipulation in S_k, bounding checkpoints usable, no glare -> DET, ATTR_STAGE(k)
        - Checkpoint bounding manipulation interval degraded or unusable -> DEG, ATTR_ABSTAIN_DEGRADED
        - Defect deliberately hidden by glare at both bounding checkpoints -> IND, ATTR_ABSTAIN_INDISTINGUISHABLE
    """
    interval_raw = str(staging_row.get("manipulation_interval", "none")).strip().upper()
    glare_flag = str(staging_row.get("glare_over_defect", "no")).strip().lower() == "yes"
    degraded_cp = str(staging_row.get("degraded_checkpoint", "none")).strip().lower()
    has_staged_degradation = degraded_cp not in ("none", "", "null", "false")
    is_capture_degraded = not capture_quality_passed

    # 1. Deliberate Glare Concealment -> INDISTINGUISHABLE
    if glare_flag:
        return ("OBS_INDISTINGUISHABLE", "ATTR_ABSTAIN_INDISTINGUISHABLE", None)

    # 2. Degraded Observation Telemetry -> DEGRADED
    if has_staged_degradation or is_capture_degraded:
        return ("OBS_DEGRADED_INCOMPLETE", "ATTR_ABSTAIN_DEGRADED", None)

    # Under field mask, intermediate checkpoints (CP2, CP3) have no scale readings.
    # If a staged manipulation has weight change but no visual or seal tamper,
    # intermediate bounding checkpoints lack the required modality evidence to localize.
    if mask == "field" and interval_raw.startswith("S") and len(interval_raw) >= 2:
        is_weight_only = (
            staging_row.get("evidence_modality") == "weight_only"
            or (
                str(staging_row.get("weight_matched", "no")).strip().lower() == "no"
                and str(staging_row.get("seal_tampered", "no")).strip().lower() == "no"
                and str(staging_row.get("visual_defect", "no")).strip().lower() == "no"
                and "weight_only" in str(staging_row.get("actual_manipulation", "")).lower()
            )
        )
        if is_weight_only:
            return ("OBS_DEGRADED_INCOMPLETE", "ATTR_ABSTAIN_DEGRADED", None)

    # 3. Legitimate / Intact Transit -> CONFIRMED LEGITIMATE
    if interval_raw in ("NONE", "INTACT"):
        return ("OBS_DETERMINABLE", "ATTR_CONFIRMED_LEGITIMATE", [1, 4])

    # 4. Determinable Stage Manipulation S_k
    stage_map = {
        1: "ATTR_STAGE_FORWARD_TRANSIT",
        2: "ATTR_STAGE_CONSUMER_CUSTODY",
        3: "ATTR_STAGE_REVERSE_TRANSIT",
    }
    if interval_raw.startswith("S") and len(interval_raw) >= 2:
        try:
            stage_k = int(interval_raw[1])
            expected_label = stage_map.get(stage_k, f"ATTR_STAGE_{stage_k}")
            return ("OBS_DETERMINABLE", expected_label, [stage_k, stage_k + 1])
        except ValueError:
            pass

    # Fallback to degraded if interval string is malformed
    return ("OBS_DEGRADED_INCOMPLETE", "ATTR_ABSTAIN_DEGRADED", None)


def get_determinability_rule_hash() -> str:
    """
    Compute cryptographic SHA-256 digest of this determinability rule's source code.
    Committed into the public repository prior to study capture (Gate G-2).
    """
    source_bytes = Path(__file__).read_bytes()
    return hashlib.sha256(source_bytes).hexdigest()
