from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from trinetra_link.config import RESTRICTED_DATA_DIR

DEFAULT_STAGING_LOG_CSV = RESTRICTED_DATA_DIR / "staging_log_120.csv"

FIELDNAMES = [
    "journey_code",
    "assigned_cell",
    "actual_manipulation",
    "manipulation_interval",
    "degraded_checkpoint",
    "degradation_type",
    "glare_over_defect",
    "overhead_video_file",
    "overhead_video_sha256",
    "deviation_notes",
    "stager_id",
    "timestamp_utc",
]


class StagingLogRecord(BaseModel):
    journey_code: str
    assigned_cell: str
    actual_manipulation: str
    manipulation_interval: str = Field(..., description="S1, S2, S3, or none")
    degraded_checkpoint: str = Field(default="none", description="none, CP1, CP2, CP3, or CP4")
    degradation_type: str = Field(default="none", description="none, dark, scale_error, blur, missing")
    glare_over_defect: str = Field(default="no", description="yes or no")
    overhead_video_file: Optional[str] = None
    overhead_video_sha256: Optional[str] = None
    deviation_notes: str = ""
    stager_id: str
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def append_staging_log_entry(
    entry: StagingLogRecord,
    log_path: Optional[Path | str] = None,
) -> Path:
    """Append a physically filmed staging record to the access-controlled log."""
    path = Path(log_path) if log_path else DEFAULT_STAGING_LOG_CSV
    path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = path.exists()

    # Verify no duplicate entry for journey_code
    if file_exists:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("journey_code") == entry.journey_code:
                    raise ValueError(f"Staging log already contains entry for {entry.journey_code} (append-only)")

    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry.model_dump())

    return path


def load_staging_log(log_path: Optional[Path | str] = None) -> List[Dict[str, str]]:
    """Load all records from the staging log."""
    path = Path(log_path) if log_path else DEFAULT_STAGING_LOG_CSV
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
