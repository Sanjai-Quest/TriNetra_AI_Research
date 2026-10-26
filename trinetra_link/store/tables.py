from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class JourneyRecord(SQLModel, table=True):
    __tablename__ = "journeys"

    journey_code: str = Field(primary_key=True, index=True)
    status: str = Field(default="ACTIVE")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata_json: str = Field(default="{}")


class CheckpointRecord(SQLModel, table=True):
    __tablename__ = "checkpoints"

    id: Optional[int] = Field(default=None, primary_key=True)
    journey_code: str = Field(index=True)
    cp_index: int = Field(index=True)
    ts_utc: datetime
    device_id: str
    operator_id: str
    weights_json: str
    scale_id: str
    scale_status: str
    calibration_date: Optional[str] = None
    images_json: str = Field(default="[]")
    seal_qr: Optional[str] = None
    serial: Optional[str] = None
    imei: Optional[str] = None
    carrier_log: Optional[str] = None
    permitted_packaging_change: bool = False
    tare_delta_g: float = 0.0
    app_version: str = "2.6.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QualityRecord(SQLModel, table=True):
    __tablename__ = "quality_reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    journey_code: str = Field(index=True)
    cp_index: int = Field(index=True)
    q_k: float
    feature_scores_json: str
    passed: bool
    reasons_json: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReconcileRecord(SQLModel, table=True):
    __tablename__ = "reconcile_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    journey_code: str = Field(index=True)
    cp_index: int = Field(index=True)
    weight_anomaly: bool
    weight_delta_g: float
    identity_anomaly: bool
    identity_mismatches_json: str
    visual_anomaly: bool
    visual_scores_json: str
    fused_state: str
    trusted_modalities_json: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AttributionRecord(SQLModel, table=True):
    __tablename__ = "attributions"

    id: Optional[int] = Field(default=None, primary_key=True)
    journey_code: str = Field(index=True)
    label: str
    posterior_json: str
    interval_json: Optional[str] = None
    trusted_set_json: str
    per_modality_evidence_json: str
    rationale_text: str
    decision: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StagingTruthRecord(SQLModel, table=True):
    """Restricted truth table stored strictly in data/restricted/truth.sqlite."""
    __tablename__ = "ground_truth"

    journey_code: str = Field(primary_key=True, index=True)
    scenario_id: str
    cell_id: str
    nominal_weight_g: float
    planned_tamper_stage: Optional[int] = None
    actual_tamper_stage: Optional[int] = None
    tamper_type: Optional[str] = None
    video_sha256: Optional[str] = None
    expected_label: str
    determinability: str
    salt: Optional[str] = None
    commitment_hash: Optional[str] = None
    staged_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
