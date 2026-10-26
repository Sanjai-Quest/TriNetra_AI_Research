from __future__ import annotations

import csv
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from trinetra_link.config import REPO_ROOT
from trinetra_link.demo.make_synthetic_dryrun import generate_synthetic_dryrun_dataset
from trinetra_link.eval.e1 import evaluate_e1
from trinetra_link.viewer.app import create_viewer_app


@pytest.fixture(scope="module")
def synthetic_dataset():
    """Ensure synthetic dataset is generated and return its metadata."""
    demo_dir = REPO_ROOT / "demo_data" / "synthetic_120"
    if not (demo_dir / "store.db").exists():
        res = generate_synthetic_dryrun_dataset(output_dir=demo_dir, scale_sigma=1.0, seed=777)
    else:
        res = {
            "output_dir": str(demo_dir),
            "split_manifest": str(demo_dir / "split_manifest.json"),
            "staging_log": str(demo_dir / "staging_log_120.csv"),
            "assignment_csv": str(demo_dir / "staging_assignment_120.csv"),
            "scales_json": str(demo_dir / "scales.json"),
            "ground_truth_json": str(demo_dir / "ground_truth_120.json"),
        }
    return res


def test_synthetic_dataset_cell_distribution_and_tags(synthetic_dataset):
    assign_csv = Path(synthetic_dataset["assignment_csv"])
    assert assign_csv.exists()

    with open(assign_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 120

    # Verify all journey codes carry "SYN-"
    for r in rows:
        assert r["journey_code"].startswith("SYN-2026-")
        assert r["synthetic"] in ("True", "true", True)

    # Verify 8 scenario cells quotas
    cell_counts = {}
    for r in rows:
        c = r["assigned_cell"]
        cell_counts[c] = cell_counts.get(c, 0) + 1

    expected_quotas = {
        "intact": 30,
        "permitted_flyer": 12,
        "forward_transit_damage": 14,
        "doorstep_substitution": 14,
        "customer_tamper": 14,
        "reverse_transit_tamper": 12,
        "degraded_evidence": 12,
        "ambiguous_evidence": 12,
    }
    assert cell_counts == expected_quotas


def test_synthetic_split_manifest_stratification(synthetic_dataset):
    manifest_path = Path(synthetic_dataset["split_manifest"])
    assert manifest_path.exists()

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["synthetic"] is True
    assert data["total_journeys"] == 120
    assert data["calibration_count"] == 24
    assert data["test_count"] == 96
    assert len(data["calibration_journey_codes"]) == 24
    assert len(data["test_journey_codes"]) == 96


def test_synthetic_degraded_and_glare_handling(synthetic_dataset):
    staging_csv = Path(synthetic_dataset["staging_log"])
    assert staging_csv.exists()

    with open(staging_csv, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    degraded_rows = [r for r in rows if r["assigned_cell"] == "degraded_evidence"]
    ambiguous_rows = [r for r in rows if r["assigned_cell"] == "ambiguous_evidence"]

    assert len(degraded_rows) == 12
    assert len(ambiguous_rows) == 12

    for r in degraded_rows:
        assert r["degraded_checkpoint"] in ("cp2", "cp3")
        assert r["degradation_type"] == "scale_error"

    for r in ambiguous_rows:
        assert r["glare_over_defect"] == "yes"


def test_evaluator_strictly_refuses_synthetic_data_without_flag(synthetic_dataset):
    """The experiment runner must refuse demo_data/ without --allow-synthetic-dry-run."""
    manifest_path = synthetic_dataset["split_manifest"]
    staging_log_path = synthetic_dataset["staging_log"]

    with pytest.raises(RuntimeError) as exc_info:
        evaluate_e1(
            split_manifest_path=manifest_path,
            staging_log_path=staging_log_path,
            allow_synthetic_dry_run=False,  # Refused by default!
        )

    assert "REFUSAL TO EXECUTE ON SYNTHETIC DEMO DATA" in str(exc_info.value)


def test_evaluator_watermarks_when_allowed(synthetic_dataset, tmp_path):
    """When allow_synthetic_dry_run=True, execution succeeds and watermarks all outputs."""
    out_dir = tmp_path / "synthetic_run"
    manifest_path = synthetic_dataset["split_manifest"]
    staging_log_path = synthetic_dataset["staging_log"]
    scales_path = synthetic_dataset["scales_json"]

    res = evaluate_e1(
        split_manifest_path=manifest_path,
        staging_log_path=staging_log_path,
        scales_path=scales_path,
        output_dir=out_dir,
        b_bootstrap=50,  # Fast resamples for test
        allow_synthetic_dry_run=True,
        is_demo_run=True,
        skip_llm_if_no_key=True,
    )

    csv_path = Path(res["artifacts"]["csv_table"])
    latex_path = Path(res["artifacts"]["latex_table"])
    prov_path = out_dir / "provenance.json"

    assert csv_path.exists()
    assert latex_path.exists()
    assert prov_path.exists()

    # Check watermarks
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "SYNTHETIC DRY RUN — NOT A RESULT" in csv_text

    latex_text = latex_path.read_text(encoding="utf-8")
    assert "SYNTHETIC DRY RUN — NOT A RESULT" in latex_text

    with open(prov_path, "r", encoding="utf-8") as fp:
        prov = json.load(fp)
    assert prov["watermark"] == "SYNTHETIC DRY RUN — NOT A RESULT"
    assert prov["synthetic_dry_run"] is True


def test_viewer_demo_mode_api_and_blinding():
    demo_db = REPO_ROOT / "demo_data" / "synthetic_120" / "store.db"
    app = create_viewer_app(db_path=demo_db, demo_mode=True)
    client = TestClient(app)

    # 1. Health check reports demo mode
    h_resp = client.get("/health")
    assert h_resp.status_code == 200
    assert h_resp.json()["demo_mode"] is True

    # 2. Journeys list flags synthetic
    j_resp = client.get("/api/journeys")
    assert j_resp.status_code == 200
    j_list = j_resp.json()
    assert len(j_list) >= 120
    assert all(j["journey_code"].startswith("SYN-2026-") for j in j_list)
    assert all(j["is_synthetic"] is True for j in j_list)

    # 3. Blinded journey detail
    first_code = j_list[0]["journey_code"]
    det_resp = client.get(f"/api/journeys/{first_code}")
    assert det_resp.status_code == 200
    detail = det_resp.json()
    assert detail["journey_code"] == first_code
    assert detail["is_synthetic"] is True
    assert len(detail["checkpoints"]) == 4

    # Blinding guarantee: restricted staging fields must NEVER leak
    leakage_keys = {
        "assigned_cell", "actual_manipulation", "manipulation_interval",
        "degradation_type", "glare_over_defect", "overhead_video_sha256",
        "stager_id", "staged_by", "omega_star", "expected_label", "ground_truth_interval"
    }
    for k in leakage_keys:
        assert k not in detail

    # 4. Image endpoint serves rendered photographs
    photo = detail["checkpoints"][0]["photos"][0]
    img_resp = client.get(photo["url"])
    assert img_resp.status_code == 200
    assert len(img_resp.content) > 500  # Valid JPEG binary

    # 5. HTML includes synthetic banner
    page_resp = client.get("/")
    assert page_resp.status_code == 200
    assert "syntheticBanner" in page_resp.text
    assert "banner-synthetic" in page_resp.text
    assert "SYNTHETIC DRY RUN DEMO" in page_resp.text
