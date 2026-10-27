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
    """Ensure exact canonical label format across all methods."""
    lbl = label.strip()
    if lbl in ("LEGITIMATE", "ATTR_CONFIRMED_LEGITIMATE"):
        return "ATTR_CONFIRMED_LEGITIMATE"
    if lbl in ("ABSTAIN_DEGRADED", "ATTR_ABSTAIN_DEGRADED"):
        return "ATTR_ABSTAIN_DEGRADED"
    if lbl in ("ABSTAIN_INDISTINGUISHABLE", "ATTR_ABSTAIN_INDISTINGUISHABLE"):
        return "ATTR_ABSTAIN_INDISTINGUISHABLE"
    if lbl in ("ATTR_STAGE(1)", "STAGE(1)", "ATTR_STAGE_1", "STAGE_1", "ATTR_STAGE_FORWARD_TRANSIT"):
        return "ATTR_STAGE_FORWARD_TRANSIT"
    if lbl in ("ATTR_STAGE(2)", "STAGE(2)", "ATTR_STAGE_2", "STAGE_2", "ATTR_STAGE_CONSUMER_CUSTODY"):
        return "ATTR_STAGE_CONSUMER_CUSTODY"
    if lbl in ("ATTR_STAGE(3)", "STAGE(3)", "ATTR_STAGE_3", "STAGE_3", "ATTR_STAGE_REVERSE_TRANSIT"):
        return "ATTR_STAGE_REVERSE_TRANSIT"
    return lbl


def predict_trinetra_link(
    journey: Journey,
    mode: str = "algorithm1",
    theta: float = 0.70,
    tau: float = 0.80,
    z_weight: float = 3.0,
    visual_threshold: float = 0.25,
    scales_config: Optional[Dict[str, Any]] = None,
    scales_path: Optional[Path | str] = None,
    disable_quality_gate: bool = False,
    disable_visual: bool = False,
    fixed_weight_threshold: Optional[float] = None,
) -> Attribution:
    """
    Run full TriNetra-Link pipeline on a journey:
      1. Quality Gate evaluations -> q_k in [0, 1] per modality (photo, weight, seal)
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

    # Pass scales_config to QualityGate so scale_sigma is known
    gate_cfg = None
    if scales_config:
        gate_cfg = {"scale": {"scales": scales_config.get("scales", {}), "sigma_g": 1.0}}
    gate = QualityGate(config=gate_cfg, theta=theta)
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
                feature_scores={
                    "q_scale": 1.0,
                    "q_weight": 1.0,
                    "q_temporal": 1.0,
                    "q_seal": 1.0,
                    "q_image": 1.0,
                    "q_photo": 1.0,
                },
                passed=True,
                reasons=[],
            )
        else:
            prev_cp = cps.get(k - 1) if k > 1 else None
            qr = gate.evaluate(cp, previous_observation=prev_cp)

        q_reports[k] = qr
        q_k[k] = qr.q_k

    # 2. Multimodal Reconciliation
    z_k: Dict[int, str] = {1: "INTACT"}
    modality_evidence: Dict[int, Dict[str, Tuple[str, float]]] = {}

    for k in (2, 3, 4):
        cp_k = cps.get(k)
        if not cp_k:
            z_k[k] = "UNK"
            continue

        qr = q_reports[k]
        q_weight = qr.feature_scores.get("q_weight", qr.feature_scores.get("q_scale", 1.0))
        q_seal = qr.feature_scores.get("q_seal", qr.feature_scores.get("q_temporal", 1.0))
        q_photo = qr.feature_scores.get("q_photo", qr.feature_scores.get("q_image", 1.0))

        # Weight test
        tare_delta = sum(
            cp.tare_delta_g
            for cp in journey.checkpoints
            if cp.cp_index <= k and cp.permitted_packaging_change
        )
        if fixed_weight_threshold is not None:
            w1 = float(np.mean(cp1.weights_g)) if cp1.weights_g else 0.0
            wk = float(np.mean(cp_k.weights_g)) if cp_k.weights_g else 0.0
            weight_diff = abs(wk - w1 - tare_delta)
            weight_anom = weight_diff > fixed_weight_threshold
            delta_w = weight_diff
        else:
            weight_anom, delta_w, _ = reconcile_weights(
                obs_baseline=cp1,
                obs_current=cp_k,
                z=z_weight,
                scales_file_path=scales_path,
                cumulative_tare_delta_g=tare_delta,
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

        # Per-modality trust determinations:
        # A bad weight reading does not make photos or seal untrusted
        trusted_weight = (
            (q_weight >= theta)
            and (weight_anom != "UNKNOWN")
            and bool(cp_k.weights_g)
            and bool(cp1.weights_g)
            and cp_k.scale_status in ("OK", "MANUAL", "SETTLED")
        )
        trusted_seal = (q_seal >= theta) and bool(cp_k.seal_qr or cp_k.serial or cp_k.imei)
        trusted_photo = (q_photo >= theta) and bool(cp_k.images) and not disable_visual

        weight_obs = "ANOM" if weight_anom is True else ("INTACT" if weight_anom is False else "UNK")
        seal_obs = "ANOM" if identity_anom else "INTACT"
        photo_obs = "ANOM" if visual_anom else "INTACT"

        modality_evidence[k] = {
            "weight": (weight_obs if trusted_weight else "UNK", q_weight if trusted_weight else 0.0),
            "seal": (seal_obs if trusted_seal else "UNK", q_seal if trusted_seal else 0.0),
            "photo": (photo_obs if trusted_photo else "UNK", q_photo if trusted_photo else 0.0),
        }

        anomalies_present = []
        agreements_present = []

        if trusted_weight:
            (anomalies_present if weight_anom is True else agreements_present).append("weight")
        if trusted_seal:
            (anomalies_present if identity_anom else agreements_present).append("seal")
        if trusted_photo:
            (anomalies_present if visual_anom else agreements_present).append("photo")

        if anomalies_present:
            z_k[k] = "ANOM"
        elif agreements_present:
            z_k[k] = "INTACT"
        else:
            z_k[k] = "UNK"

        # Checkpoint trust in T: trusted if at least one modality provides trusted observation
        trusted_mod_scores = [q for (obs, q) in modality_evidence[k].values() if q >= theta]
        q_k[k] = max(trusted_mod_scores) if trusted_mod_scores else 0.0

    # 3. Attribution Rule Selection
    if mode == "bayes":
        attr = attribute_bayes(
            journey_code=code,
            q_k=q_k,
            z_k=z_k,
            tau=tau,
            theta=theta,
            modality_evidence=modality_evidence,
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
