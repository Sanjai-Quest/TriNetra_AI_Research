from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np

from trinetra_link.attribution.bayes import attribute_bayes
from trinetra_link.attribution.interval import attribute_interval_algorithm_1
from trinetra_link.quality.gate import QualityGate
from trinetra_link.reconcile.fuse import fuse_checkpoint_observations
from trinetra_link.reconcile.identity import reconcile_identity
from trinetra_link.reconcile.visual import reconcile_visual
from trinetra_link.reconcile.weight import reconcile_weights
from trinetra_link.schema.models import Attribution, CheckpointObservation, Journey, QualityReport


def canonicalize_label(label: str) -> str:
    """Ensure consistent ATTR_* prefix across all attribution methods."""
    lbl = label.strip()
    if lbl in ("LEGITIMATE", "ATTR_CONFIRMED_LEGITIMATE"):
        return "ATTR_CONFIRMED_LEGITIMATE"
    if lbl in ("ABSTAIN_DEGRADED", "ATTR_ABSTAIN_DEGRADED"):
        return "ATTR_ABSTAIN_DEGRADED"
    if lbl in ("ABSTAIN_INDISTINGUISHABLE", "ATTR_ABSTAIN_INDISTINGUISHABLE"):
        return "ATTR_ABSTAIN_INDISTINGUISHABLE"
    if lbl.startswith("STAGE(") and not lbl.startswith("ATTR_"):
        return f"ATTR_{lbl}"
    return lbl


def predict_trinetra_link(
    journey: Journey,
    mode: str = "algorithm1",
    theta: float = 0.70,
    tau: float = 0.80,
    z_weight: float = 3.0,
    visual_threshold: float = 0.25,
    scales_config: Optional[Dict[str, Any]] = None,
    disable_quality_gate: bool = False,
    disable_visual: bool = False,
    fixed_weight_threshold: Optional[float] = None,
) -> Attribution:
    """
    Run full TriNetra-Link pipeline on a journey:
      1. Quality Gate evaluations -> q_k in [0, 1]
      2. Multimodal physical reconciliation vs CP1 baseline -> z_k in {INTACT, ANOM, UNK}
      3. Attribution rule (Algorithm 1 or Bayesian posterior coalescence)
    Supports ablation configurations:
      - disable_quality_gate: forces all q_k = 1.0
      - disable_visual: ignores visual reconciler anomalies
      - fixed_weight_threshold: replaces scale noise model with constant grams threshold
    """
    code = journey.journey_code
    cps = {cp.cp_index: cp for cp in journey.checkpoints}
    cp1 = cps.get(1)

    if not cp1 or len(cps) < 4:
        return Attribution(
            journey_code=code,
            label="ATTR_ABSTAIN_DEGRADED",
            rationale_text="Missing or incomplete checkpoint observations (fewer than 4 checkpoints).",
        )

    gate = QualityGate(theta=theta)
    q_reports: Dict[int, QualityReport] = {}
    q_k: Dict[int, float] = {}

    # 1. Quality Gate evaluation
    for k in (1, 2, 3, 4):
        cp = cps.get(k)
        if not cp:
            q_k[k] = 0.0
            continue

        if disable_quality_gate:
            qr = QualityReport(
                journey_code=code,
                cp_index=k,
                q_k=1.0,
                feature_scores={"q_scale": 1.0, "q_temporal": 1.0, "q_image": 1.0},
                passed=True,
                reasons=[],
            )
        else:
            qr = gate.evaluate(cp)

        q_reports[k] = qr
        q_k[k] = qr.q_k

    # 2. Multimodal Reconciliation
    z_k: Dict[int, str] = {1: "INTACT"}

    for k in (2, 3, 4):
        cp_k = cps.get(k)
        if not cp_k:
            z_k[k] = "UNK"
            continue

        qr = q_reports[k]

        # Weight test
        if fixed_weight_threshold is not None:
            tare_k = sum(
                cp.tare_delta_g
                for cp in journey.checkpoints
                if cp.cp_index <= k and cp.permitted_packaging_change
            )
            w1 = float(np.mean(cp1.weights_g)) if cp1.weights_g else 0.0
            wk = float(np.mean(cp_k.weights_g)) if cp_k.weights_g else 0.0
            weight_diff = abs(wk - w1 - tare_k)
            weight_anom = weight_diff > fixed_weight_threshold
            delta_w = weight_diff
        else:
            # Standard scale-calibrated weight test
            scale_sigma = 0.03
            scale_delta = 0.05
            if scales_config and "scales" in scales_config:
                sc_info = scales_config["scales"].get(cp_k.scale_id, {})
                scale_sigma = sc_info.get("sigma_g", 0.03)
                scale_delta = sc_info.get("delta_g", 0.05)

            tare_delta = sum(
                cp.tare_delta_g
                for cp in journey.checkpoints
                if cp.cp_index <= k and cp.permitted_packaging_change
            )
            weight_anom, delta_w, _ = reconcile_weights(
                obs_baseline=cp1,
                obs_current=cp_k,
                z=z_weight,
            )

        # Identity test
        identity_anom, mismatches = reconcile_identity(obs_baseline=cp1, obs_current=cp_k)

        # Visual test
        if disable_visual:
            visual_anom = False
            visual_scores = {}
        else:
            visual_anom, visual_scores = reconcile_visual(
                obs_baseline=cp1,
                obs_current=cp_k,
                visual_threshold=visual_threshold,
            )

        # Modality fusion
        trusted_weight = qr.feature_scores.get("q_scale", 1.0) >= theta
        trusted_ident = qr.feature_scores.get("q_temporal", 1.0) >= theta
        trusted_vis = qr.feature_scores.get("q_image", 1.0) >= theta

        anomalies_present = []
        agreements_present = []

        if trusted_weight:
            (anomalies_present if weight_anom else agreements_present).append("weight")
        if trusted_ident:
            (anomalies_present if identity_anom else agreements_present).append("identity")
        if trusted_vis and not disable_visual:
            (anomalies_present if visual_anom else agreements_present).append("visual")

        if anomalies_present:
            z_k[k] = "ANOM"
        elif agreements_present and qr.q_k >= theta:
            z_k[k] = "INTACT"
        else:
            z_k[k] = "UNK"

    # 3. Attribution Rule Selection
    if mode == "bayes":
        attr = attribute_bayes(
            journey_code=code,
            q_k=q_k,
            z_k=z_k,
            tau=tau,
        )
    else:
        # Default: Algorithm 1 (deterministic interval attribution)
        attr = attribute_interval_algorithm_1(
            journey_code=code,
            q_k=q_k,
            z_k=z_k,
            theta=theta,
        )

    # Standardize label output
    attr.label = canonicalize_label(attr.label)
    return attr
