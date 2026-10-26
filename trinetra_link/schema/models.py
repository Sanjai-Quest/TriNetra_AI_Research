from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ImageRef(BaseModel):
    """Reference to a captured photographic evidence asset."""
    side: str = Field(..., description="Surface identifier e.g. front, back, top, seal")
    path: str = Field(..., description="Repository-relative or media storage path")
    sha256: str = Field(..., description="SHA-256 digest of the image bytes")
    w: int = Field(..., ge=1, description="Image pixel width")
    h: int = Field(..., ge=1, description="Image pixel height")
    exposure: Optional[float] = Field(default=None, description="EXIF exposure time in seconds if available")


class CheckpointObservation(BaseModel):
    """Observation recorded at physical checkpoint k in 1..K."""
    journey_code: str = Field(..., description="Unique journey code, e.g. JRN-2026-0001")
    cp_index: int = Field(..., ge=1, le=10, description="Checkpoint sequence index 1..K")
    ts_utc: datetime = Field(..., description="Timestamp of observation in UTC")
    device_id: str = Field(..., description="Capturing device UUID or identifier")
    operator_id: str = Field(..., description="Capture operator identifier")
    weights_g: List[float] = Field(default_factory=list, description="Repeated weight readings in grams (>= 3)")
    scale_id: str = Field(..., description="Identifier of the scale used")
    scale_status: str = Field(default="OK", description="Status code from scale, e.g. OK, MANUAL, UNSTABLE, ERROR")
    calibration_date: Optional[str] = Field(default=None, description="Last calibration date (YYYY-MM-DD)")
    images: List[ImageRef] = Field(default_factory=list, description="Photographic assets captured at this checkpoint")
    seal_qr: Optional[str] = Field(default=None, description="Decoded payload of the tamper-evident security seal QR")
    serial: Optional[str] = Field(default=None, description="Observed serial number")
    imei: Optional[str] = Field(default=None, description="Observed IMEI for serialized cellular hardware")
    carrier_log: Optional[str] = Field(default=None, description="Optional custody carrier log notes")
    permitted_packaging_change: bool = Field(default=False, description="Whether legitimate re-boxing or re-taping occurred")
    tare_delta_g: float = Field(default=0.0, description="Known tare delta in grams for permitted packaging modifications")
    app_version: str = Field(default="2.6.0", description="Software version used for capture")

    @field_validator("weights_g")
    @classmethod
    def validate_weights(cls, v: List[float]) -> List[float]:
        if any(w < 0 for w in v):
            raise ValueError("Weight readings cannot be negative")
        return v


class Journey(BaseModel):
    """Complete multi-checkpoint journey container."""
    journey_code: str = Field(..., description="Canonical journey identifier")
    status: str = Field(default="ACTIVE", description="Journey status: ACTIVE, COMPLETED, ABSTAINED")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    checkpoints: List[CheckpointObservation] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QualityReport(BaseModel):
    """Evaluation output from the quality gate for checkpoint k."""
    journey_code: str
    cp_index: int
    q_k: float = Field(..., ge=0.0, le=1.0, description="Combined quality factor in [0, 1]")
    feature_scores: Dict[str, float] = Field(default_factory=dict)
    passed: bool = Field(..., description="Whether q_k >= theta threshold")
    reasons: List[str] = Field(default_factory=list)


class ReconcileResult(BaseModel):
    """Multimodal physical reconciliation output vs baseline CP1."""
    journey_code: str
    cp_index: int
    weight_anomaly: bool = False
    weight_delta_g: float = 0.0
    identity_anomaly: bool = False
    identity_mismatches: List[str] = Field(default_factory=list)
    visual_anomaly: bool = False
    visual_scores: Dict[str, float] = Field(default_factory=dict)
    fused_state: str = Field(..., description="INTACT, ANOM, or UNK")
    trusted_modalities: List[str] = Field(default_factory=list)


class Attribution(BaseModel):
    """Stage-level chain-of-custody attribution output."""
    journey_code: str
    label: str = Field(..., description="LEGITIMATE, STAGE(a), ABSTAIN_DEGRADED, or ABSTAIN_INDISTINGUISHABLE")
    posterior: Dict[str, float] = Field(default_factory=dict, description="Posterior probability per stage")
    interval: Optional[List[int]] = Field(default=None, description="Attributed interval [a, b]")
    trusted_set: List[int] = Field(default_factory=list, description="Set of checkpoints with q_k >= theta")
    per_modality_evidence: Dict[str, Any] = Field(default_factory=dict)
    rationale_text: str = Field(..., description="Human-readable causal explanation")
    decision: Optional[str] = Field(default=None, description="Normative operational decision e.g. DEC_REFUND")


class StagingLogEntry(BaseModel):
    """Physically staged scenario log entry (Restricted Data)."""
    journey_code: str
    scenario_id: str
    cell_id: str
    nominal_weight_g: float
    planned_tamper_stage: Optional[int] = None
    actual_tamper_stage: Optional[int] = None
    tamper_type: Optional[str] = None
    video_sha256: Optional[str] = None
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    staged_by: str = Field(...)


class GroundTruth(BaseModel):
    """Derived physical ground truth (Restricted Data)."""
    journey_code: str
    expected_label: str
    determinability: str = Field(..., description="OBS_DETERMINABLE, OBS_DEGRADED_INCOMPLETE, OBS_INDISTINGUISHABLE")
    tamper_interval: Optional[List[int]] = None
    salt: Optional[str] = None
    commitment_hash: Optional[str] = None
