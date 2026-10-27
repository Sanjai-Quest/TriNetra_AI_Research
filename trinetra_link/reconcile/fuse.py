from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np

from trinetra_link.quality.gate import QualityGate
from trinetra_link.reconcile.identity import reconcile_identity
from trinetra_link.reconcile.visual import reconcile_visual
from trinetra_link.reconcile.weight import reconcile_weights
from trinetra_link.schema.models import CheckpointObservation, QualityReport, ReconcileResult


def fuse_checkpoint_observations(
    obs_baseline: CheckpointObservation,
    obs_current: CheckpointObservation,
    quality_report: QualityReport,
    z_weight: float = 3.0,
    visual_threshold: float = 0.25,
    theta: float = 0.70,
    scales_file_path: Optional[str] = None,
    image_arrays_baseline: Optional[Dict[str, np.ndarray]] = None,
    image_arrays_current: Optional[Dict[str, np.ndarray]] = None,
) -> ReconcileResult:
    """
    Multimodal fusion reconciler.
    Fused state z_k:
      - 'ANOM'   if any trusted modality flags a change vs. CP1
      - 'INTACT' if all trusted modalities agree with CP1
      - 'UNK'    if no modalities are trusted (or uninformative)
    """
    scores = quality_report.feature_scores

    # 1. Determine trusted modalities based on quality scores
    trusted_modalities: List[str] = []

    # Scale / weight trust
    q_weight = scores.get("q_weight", scores.get("q_scale", 1.0))
    if q_weight >= theta and obs_baseline.weights_g and obs_current.weights_g:
        trusted_modalities.append("weight")

    # Identity trust: serial or QR present and temporal order intact
    q_temp = scores.get("q_seal", scores.get("q_temporal", 1.0))
    if q_temp >= theta and (obs_current.serial or obs_current.seal_qr or obs_current.imei):
        trusted_modalities.append("identity")

    # Visual trust
    q_image = scores.get("q_photo", scores.get("q_image", 1.0))
    if q_image >= theta and obs_current.images:
        trusted_modalities.append("visual")

    # 2. Reconcile modalities
    # Weight
    weight_anom, delta_w, bound_w = reconcile_weights(
        obs_baseline=obs_baseline,
        obs_current=obs_current,
        z=z_weight,
        scales_file_path=scales_file_path,
    )
    if weight_anom == "UNKNOWN" and "weight" in trusted_modalities:
        trusted_modalities.remove("weight")

    # Identity
    id_anom, mismatches = reconcile_identity(
        obs_baseline=obs_baseline,
        obs_current=obs_current,
    )

    # Visual
    vis_anom, vis_scores = reconcile_visual(
        obs_baseline=obs_baseline,
        obs_current=obs_current,
        visual_threshold=visual_threshold,
        image_arrays_a=image_arrays_baseline,
        image_arrays_b=image_arrays_current,
    )

    # 3. Apply fusion logic
    if not trusted_modalities:
        fused_state = "UNK"
    else:
        anomalies_in_trusted = []
        if "weight" in trusted_modalities and weight_anom is True:
            anomalies_in_trusted.append("weight")
        if "identity" in trusted_modalities and id_anom:
            anomalies_in_trusted.append("identity")
        if "visual" in trusted_modalities and vis_anom:
            anomalies_in_trusted.append("visual")

        if anomalies_in_trusted:
            fused_state = "ANOM"
        else:
            fused_state = "INTACT"

    return ReconcileResult(
        journey_code=obs_current.journey_code,
        cp_index=obs_current.cp_index,
        weight_anomaly=weight_anom,
        weight_delta_g=delta_w,
        identity_anomaly=id_anom,
        identity_mismatches=mismatches,
        visual_anomaly=vis_anom,
        visual_scores=vis_scores,
        fused_state=fused_state,
        trusted_modalities=trusted_modalities,
    )
