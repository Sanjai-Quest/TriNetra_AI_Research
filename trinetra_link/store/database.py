from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional
from sqlmodel import Session, SQLModel, create_engine, select

from trinetra_link.config import DATA_DIR, RESTRICTED_DATA_DIR
from trinetra_link.schema.models import (
    Attribution,
    CheckpointObservation,
    GroundTruth,
    ImageRef,
    Journey,
    QualityReport,
    ReconcileResult,
    StagingLogEntry,
)
from trinetra_link.store.tables import (
    AttributionRecord,
    CheckpointRecord,
    JourneyRecord,
    QualityRecord,
    ReconcileRecord,
    StagingTruthRecord,
)

DEFAULT_DB_PATH = DATA_DIR / "trinetra_store.sqlite"
DEFAULT_TRUTH_DB_PATH = RESTRICTED_DATA_DIR / "truth.sqlite"


class Store:
    """Append-only store for TriNetra-Link journeys and evidence."""

    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self._init_db()

    def _init_db(self) -> None:
        SQLModel.metadata.create_all(self.engine)

    def insert_journey(self, journey: Journey) -> None:
        with Session(self.engine) as session:
            existing = session.get(JourneyRecord, journey.journey_code)
            if existing:
                raise ValueError(f"Journey {journey.journey_code} already exists (append-only)")
            rec = JourneyRecord(
                journey_code=journey.journey_code,
                status=journey.status,
                created_at=journey.created_at,
                metadata_json=json.dumps(journey.metadata),
            )
            session.add(rec)
            session.commit()

    def get_journey(self, journey_code: str) -> Optional[Journey]:
        with Session(self.engine) as session:
            rec = session.get(JourneyRecord, journey_code)
            if not rec:
                return None
            cps = self.list_checkpoints(journey_code)
            return Journey(
                journey_code=rec.journey_code,
                status=rec.status,
                created_at=rec.created_at,
                checkpoints=cps,
                metadata=json.loads(rec.metadata_json),
            )

    def list_journeys(self) -> List[Journey]:
        with Session(self.engine) as session:
            records = session.exec(select(JourneyRecord)).all()
            return [
                Journey(
                    journey_code=r.journey_code,
                    status=r.status,
                    created_at=r.created_at,
                    checkpoints=self.list_checkpoints(r.journey_code),
                    metadata=json.loads(r.metadata_json) if r.metadata_json else {},
                )
                for r in records
            ]

    def insert_checkpoint(self, cp: CheckpointObservation) -> None:
        with Session(self.engine) as session:
            # Checkpoint index must not already exist for this journey
            query = select(CheckpointRecord).where(
                CheckpointRecord.journey_code == cp.journey_code,
                CheckpointRecord.cp_index == cp.cp_index,
            )
            if session.exec(query).first():
                raise ValueError(f"Checkpoint CP{cp.cp_index} already recorded for {cp.journey_code}")

            rec = CheckpointRecord(
                journey_code=cp.journey_code,
                cp_index=cp.cp_index,
                ts_utc=cp.ts_utc,
                device_id=cp.device_id,
                operator_id=cp.operator_id,
                weights_json=json.dumps(cp.weights_g),
                scale_id=cp.scale_id,
                scale_status=cp.scale_status,
                calibration_date=cp.calibration_date,
                images_json=json.dumps([img.model_dump() for img in cp.images]),
                seal_qr=cp.seal_qr,
                serial=cp.serial,
                imei=cp.imei,
                carrier_log=cp.carrier_log,
                permitted_packaging_change=cp.permitted_packaging_change,
                tare_delta_g=cp.tare_delta_g,
                app_version=cp.app_version,
            )
            session.add(rec)
            session.commit()

    def list_checkpoints(self, journey_code: str) -> List[CheckpointObservation]:
        with Session(self.engine) as session:
            query = select(CheckpointRecord).where(
                CheckpointRecord.journey_code == journey_code
            ).order_by(CheckpointRecord.cp_index)
            records = session.exec(query).all()
            result: List[CheckpointObservation] = []
            for r in records:
                images_raw = json.loads(r.images_json)
                images = [ImageRef(**img) for img in images_raw]
                result.append(
                    CheckpointObservation(
                        journey_code=r.journey_code,
                        cp_index=r.cp_index,
                        ts_utc=r.ts_utc,
                        device_id=r.device_id,
                        operator_id=r.operator_id,
                        weights_g=json.loads(r.weights_json),
                        scale_id=r.scale_id,
                        scale_status=r.scale_status,
                        calibration_date=r.calibration_date,
                        images=images,
                        seal_qr=r.seal_qr,
                        serial=r.serial,
                        imei=r.imei,
                        carrier_log=r.carrier_log,
                        permitted_packaging_change=r.permitted_packaging_change,
                        tare_delta_g=r.tare_delta_g,
                        app_version=r.app_version,
                    )
                )
            return result

    def insert_quality_report(self, qr: QualityReport) -> None:
        with Session(self.engine) as session:
            rec = QualityRecord(
                journey_code=qr.journey_code,
                cp_index=qr.cp_index,
                q_k=qr.q_k,
                feature_scores_json=json.dumps(qr.feature_scores),
                passed=qr.passed,
                reasons_json=json.dumps(qr.reasons),
            )
            session.add(rec)
            session.commit()

    def insert_reconcile_result(self, rr: ReconcileResult) -> None:
        with Session(self.engine) as session:
            rec = ReconcileRecord(
                journey_code=rr.journey_code,
                cp_index=rr.cp_index,
                weight_anomaly=rr.weight_anomaly,
                weight_delta_g=rr.weight_delta_g,
                identity_anomaly=rr.identity_anomaly,
                identity_mismatches_json=json.dumps(rr.identity_mismatches),
                visual_anomaly=rr.visual_anomaly,
                visual_scores_json=json.dumps(rr.visual_scores),
                fused_state=rr.fused_state,
                trusted_modalities_json=json.dumps(rr.trusted_modalities),
            )
            session.add(rec)
            session.commit()

    def insert_attribution(self, attr: Attribution) -> None:
        with Session(self.engine) as session:
            rec = AttributionRecord(
                journey_code=attr.journey_code,
                label=attr.label,
                posterior_json=json.dumps(attr.posterior),
                interval_json=json.dumps(attr.interval) if attr.interval else None,
                trusted_set_json=json.dumps(attr.trusted_set),
                per_modality_evidence_json=json.dumps(attr.per_modality_evidence),
                rationale_text=attr.rationale_text,
                decision=attr.decision,
            )
            session.add(rec)
            session.commit()
