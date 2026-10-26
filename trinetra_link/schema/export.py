"""
JSON Schema export utility for TriNetra-Link models.
"""

from __future__ import annotations

import json
from pathlib import Path
from trinetra_link.config import DOCS_DIR
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

MODELS = {
    "journey.json": Journey,
    "checkpoint_observation.json": CheckpointObservation,
    "image_ref.json": ImageRef,
    "quality_report.json": QualityReport,
    "reconcile_result.json": ReconcileResult,
    "attribution.json": Attribution,
    "staging_log_entry.json": StagingLogEntry,
    "ground_truth.json": GroundTruth,
}


def export_schemas(output_dir: Path | str | None = None) -> None:
    target_dir = Path(output_dir) if output_dir else DOCS_DIR / "schema"
    target_dir.mkdir(parents=True, exist_ok=True)

    for filename, model in MODELS.items():
        schema_path = target_dir / filename
        schema_dict = model.model_json_schema()
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2)
            f.write("\n")


if __name__ == "__main__":
    export_schemas()
