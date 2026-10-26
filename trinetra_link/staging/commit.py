from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from trinetra_link.config import REPO_ROOT, RESTRICTED_DATA_DIR
from trinetra_link.staging.determinability import derive_ground_truth, get_determinability_rule_hash
from trinetra_link.staging.log import load_staging_log

DEFAULT_MANIFEST_PATH = REPO_ROOT / "research" / "truth_manifest_v2.6.json"


def commit_ground_truth_manifest(
    staging_log_path: Optional[Path | str] = None,
    salt: Optional[str] = None,
    output_manifest_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """
    Cryptographic commitment procedure for Gate G-2 (Amendment v2.6 §6).
    Computes a salted SHA-256 hash for every journey's derived physical truth
    and records the rule code hash before capture starts.
    """
    # Salt derivation: from argument, environment, or persistent restricted secret
    if not salt:
        salt = os.getenv("TRUTH_COMMITMENT_SALT")
    if not salt:
        salt_file = RESTRICTED_DATA_DIR / ".truth_salt"
        if salt_file.exists():
            salt = salt_file.read_text(encoding="utf-8").strip()
        else:
            # Generate deterministic non-empty salt for reproducible protocol
            salt = hashlib.sha256(b"trinetra-link-v2.6.0-embargoed-salt-2026").hexdigest()
            RESTRICTED_DATA_DIR.mkdir(parents=True, exist_ok=True)
            salt_file.write_text(salt, encoding="utf-8")

    rows = load_staging_log(staging_log_path)
    if not rows:
        # Load from assignment sheet if staging log is not yet populated
        assign_csv = RESTRICTED_DATA_DIR / "staging_assignment_120.csv"
        if assign_csv.exists():
            import csv
            with open(assign_csv, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                for r in rows:
                    r["manipulation_interval"] = r.get("target_interval", "none")

    if not rows:
        raise ValueError("Cannot commit: Neither staging log nor assignment sheet found in data/restricted/")

    rule_hash = get_determinability_rule_hash()
    salt_hash = hashlib.sha256(salt.encode("utf-8")).hexdigest()

    journey_commitments: List[Dict[str, str]] = []

    for r in rows:
        code = r["journey_code"]
        omega_star, expected_label, interval = derive_ground_truth(r)
        interval_str = f"[{interval[0]},{interval[1]}]" if interval else "none"

        # Compute salted hash: salt + code + omega_star + expected_label + interval
        preimage = f"{salt}:{code}:{omega_star}:{expected_label}:{interval_str}"
        commit_hash = hashlib.sha256(preimage.encode("utf-8")).hexdigest()

        journey_commitments.append({
            "journey_code": code,
            "commitment_hash": commit_hash,
        })

    manifest = {
        "version": "2.6.0",
        "gate": "G-2",
        "committed_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_journeys": len(journey_commitments),
        "determinability_rule_sha256": rule_hash,
        "salt_hash": salt_hash,
        "journey_commitments": journey_commitments,
    }

    out_path = Path(output_manifest_path) if output_manifest_path else DEFAULT_MANIFEST_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    return {
        "manifest_path": str(out_path),
        "rule_sha256": rule_hash,
        "total_committed": len(journey_commitments),
    }
