from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import pytest
from typer.testing import CliRunner

from trinetra_link.cli import app
from trinetra_link.scale.characterise import characterise_scale, fit_scale_model, record_reference_readings
from trinetra_link.schema.models import CheckpointObservation, ImageRef, Journey
from trinetra_link.staging.assign import CELL_QUOTAS, assign_staging_cells
from trinetra_link.staging.audit import compute_rule_audit_kappa, sample_journeys_for_audit
from trinetra_link.staging.commit import commit_ground_truth_manifest
from trinetra_link.staging.determinability import derive_ground_truth, get_determinability_rule_hash
from trinetra_link.staging.log import StagingLogRecord, append_staging_log_entry, load_staging_log
from trinetra_link.staging.pilot import (
    evaluate_checkpoint_capture_quality,
    evaluate_journey_capture_quality,
    evaluate_pilot_journeys,
    load_frozen_quality_floors,
)
from trinetra_link.staging.split import CALIBRATION_QUOTAS, perform_stratified_split

runner = CliRunner()


def test_scale_characterisation_model(tmp_path: Path):
    """Test empirical Gaussian sigma and drift fitting for scale characterisation."""
    reference_data = {
        100.0: [99.98, 100.02, 100.01, 99.99, 100.00],
        500.0: [500.05, 500.02, 499.98, 500.01, 500.04],
        1000.0: [1000.10, 1000.08, 1000.05, 1000.12, 1000.07],
    }

    fit = fit_scale_model(reference_data)
    assert 0.01 <= fit["sigma_g"] <= 0.08
    assert 0.01 <= fit["delta_g"] <= 0.15

    # Test persistence to JSON
    out_json = tmp_path / "scales.json"
    res = characterise_scale("SCALE_TEST_01", reference_data, output_path=out_json)
    assert res["sigma_g"] == fit["sigma_g"]
    assert res["delta_g"] == fit["delta_g"]
    assert out_json.exists()

    with open(out_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "SCALE_TEST_01" in data["scales"]

    # Test recording reference readings
    rec_file = record_reference_readings("SCALE_TEST_01", 500.0, [500.1, 500.2, 500.0], log_dir=tmp_path / "cal")
    assert rec_file.exists()


def test_staging_assignment_quotas_and_reproducibility(tmp_path: Path):
    """Verify Amendment v2.6.0 §5 8-cell quotas and seeded reproducibility."""
    res1 = assign_staging_cells(n=120, seed=42, output_dir=tmp_path / "assign1")
    assert res1["n"] == 120
    assert len(res1["sample"]) == 3

    # Check generated files
    csv_path = Path(res1["csv_path"])
    json_path = Path(res1["json_path"])
    assert csv_path.exists()
    assert json_path.exists()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["n"] == 120
        assert data["cell_counts"] == {k: v["count"] for k, v in CELL_QUOTAS.items()}
        assert sum(data["cell_counts"].values()) == 120
        assert len(data["assignments"]) == 120

    # Test seed reproducibility
    res2 = assign_staging_cells(n=120, seed=42, output_dir=tmp_path / "assign2")
    with open(res2["json_path"], "r", encoding="utf-8") as f:
        data2 = json.load(f)
    assert data["assignments"] == data2["assignments"]

    # Test error on invalid n
    with pytest.raises(ValueError, match="received N=60"):
        assign_staging_cells(n=60, seed=42, output_dir=tmp_path)


def test_staging_log_append_only(tmp_path: Path):
    """Verify append-only integrity of physical staging log."""
    log_csv = tmp_path / "staging_log.csv"

    entry1 = StagingLogRecord(
        journey_code="JRN-2026-0001",
        assigned_cell="forward_transit_damage",
        actual_manipulation="Carton edge puncture with 5mm probe",
        manipulation_interval="S1",
        stager_id="STAGER_ALPHA",
    )
    append_staging_log_entry(entry1, log_path=log_csv)

    # Verify duplicate journey code rejected
    with pytest.raises(ValueError, match="already contains entry"):
        append_staging_log_entry(entry1, log_path=log_csv)

    entry2 = StagingLogRecord(
        journey_code="JRN-2026-0002",
        assigned_cell="intact",
        actual_manipulation="None - legitimate handling",
        manipulation_interval="none",
        stager_id="STAGER_ALPHA",
    )
    append_staging_log_entry(entry2, log_path=log_csv)

    rows = load_staging_log(log_path=log_csv)
    assert len(rows) == 2
    assert rows[0]["journey_code"] == "JRN-2026-0001"
    assert rows[1]["journey_code"] == "JRN-2026-0002"


def test_determinability_rule_and_code_hash():
    """Verify determinability rule mapping logic and cryptographic source code hash."""
    # 1. Determinability rule hash
    rule_hash = get_determinability_rule_hash()
    assert len(rule_hash) == 64
    assert all(c in "0123456789abcdef" for c in rule_hash)

    # 2. Legitimate intact
    omega, label, interval = derive_ground_truth({"manipulation_interval": "none"})
    assert omega == "OBS_DETERMINABLE"
    assert label == "ATTR_CONFIRMED_LEGITIMATE"
    assert interval == [1, 4]

    # 3. Stage 1 manipulation
    omega, label, interval = derive_ground_truth({"manipulation_interval": "S1"})
    assert omega == "OBS_DETERMINABLE"
    assert label == "ATTR_STAGE_FORWARD_TRANSIT"
    assert interval == [1, 2]

    # 4. Stage 2 manipulation
    omega, label, interval = derive_ground_truth({"manipulation_interval": "S2"})
    assert omega == "OBS_DETERMINABLE"
    assert label == "ATTR_STAGE_CONSUMER_CUSTODY"
    assert interval == [2, 3]

    # 5. Stage 3 manipulation
    omega, label, interval = derive_ground_truth({"manipulation_interval": "S3"})
    assert omega == "OBS_DETERMINABLE"
    assert label == "ATTR_STAGE_REVERSE_TRANSIT"
    assert interval == [3, 4]

    # 6. Deliberate staged degradation
    omega, label, interval = derive_ground_truth({
        "manipulation_interval": "S2",
        "degraded_checkpoint": "CP2",
        "degradation_type": "dark",
    })
    assert omega == "OBS_DEGRADED_INCOMPLETE"
    assert label == "ATTR_ABSTAIN_DEGRADED"
    assert interval is None

    # 7. Defect concealed by glare
    omega, label, interval = derive_ground_truth({
        "manipulation_interval": "S2",
        "glare_over_defect": "yes",
    })
    assert omega == "OBS_INDISTINGUISHABLE"
    assert label == "ATTR_ABSTAIN_INDISTINGUISHABLE"
    assert interval is None

    # 8. Failed capture quality check
    omega, label, interval = derive_ground_truth(
        {"manipulation_interval": "S1"},
        capture_quality_passed=False,
    )
    assert omega == "OBS_DEGRADED_INCOMPLETE"
    assert label == "ATTR_ABSTAIN_DEGRADED"


def test_truth_commitment_manifest_gate_g2(tmp_path: Path):
    """Verify cryptographic commitment procedure for Gate G-2."""
    assign_res = assign_staging_cells(n=120, seed=42, output_dir=tmp_path / "restricted")
    out_manifest = tmp_path / "truth_manifest.json"

    res = commit_ground_truth_manifest(
        staging_log_path=assign_res["csv_path"],
        salt="test-salt-secret-2026",
        output_manifest_path=out_manifest,
    )
    assert res["total_committed"] == 120
    assert len(res["rule_sha256"]) == 64

    with open(out_manifest, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["gate"] == "G-2"
        assert data["total_journeys"] == 120
        assert len(data["journey_commitments"]) == 120
        first_commit = data["journey_commitments"][0]
        assert "journey_code" in first_commit
        assert len(first_commit["commitment_hash"]) == 64


def test_stratified_split(tmp_path: Path):
    """Verify 24 calibration / 96 test stratified partition."""
    assign_res = assign_staging_cells(n=120, seed=42, output_dir=tmp_path / "restricted")
    split_manifest_path = tmp_path / "split_manifest.json"

    split_res = perform_stratified_split(
        assignments_csv_path=assign_res["csv_path"],
        seed=42,
        output_path=split_manifest_path,
    )
    assert split_res["calibration_count"] == 24
    assert split_res["test_count"] == 96

    with open(split_manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        cal_codes = set(manifest["calibration_journey_codes"])
        test_codes = set(manifest["test_journey_codes"])
        assert len(cal_codes) == 24
        assert len(test_codes) == 96
        # Disjointness
        assert len(cal_codes.intersection(test_codes)) == 0
        assert len(cal_codes.union(test_codes)) == 120
        assert manifest["calibration_by_cell"] == CALIBRATION_QUOTAS


def test_truth_audit_and_cohens_kappa(tmp_path: Path):
    """Verify 25% audit sampling and Cohen's kappa score."""
    assign_res = assign_staging_cells(n=120, seed=42, output_dir=tmp_path / "restricted")
    sample = sample_journeys_for_audit(sample_fraction=0.25, seed=101, staging_log_path=assign_res["csv_path"])
    assert len(sample) == 30

    labels_a = ["ATTR_STAGE_FORWARD_TRANSIT", "ATTR_CONFIRMED_LEGITIMATE", "ATTR_ABSTAIN_DEGRADED"]
    labels_b = ["ATTR_STAGE_FORWARD_TRANSIT", "ATTR_CONFIRMED_LEGITIMATE", "ATTR_ABSTAIN_DEGRADED"]
    kappa = compute_rule_audit_kappa(labels_a, labels_b)
    assert kappa == 1.0

    labels_c = ["ATTR_STAGE_CONSUMER_CUSTODY", "ATTR_CONFIRMED_LEGITIMATE", "ATTR_STAGE_FORWARD_TRANSIT"]
    kappa_imperfect = compute_rule_audit_kappa(labels_a, labels_c)
    assert kappa_imperfect < 1.0


def test_gate_g3_pilot_checker(tmp_path: Path):
    """Verify Gate G-3 10-journey pilot verification and frozen floors."""
    pilot_journeys = []
    for idx in range(1, 11):
        jcode = f"PILOT-{idx:02d}"
        cps = []
        for k in range(1, 5):
            cps.append(CheckpointObservation(
                journey_code=jcode,
                cp_index=k,
                ts_utc=datetime.now(timezone.utc),
                device_id="DEV_PILOT_01",
                operator_id="OP_PILOT_01",
                weights_g=[500.1, 500.2, 500.1],
                scale_id="SCALE_PILOT_01",
                scale_status="OK",
                images=[
                    ImageRef(
                        side="TOP",
                        path=f"data/pilot/{jcode}_CP{k}_TOP.jpg",
                        sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        w=1920,
                        h=1080,
                    ),
                ],
            ))
        pilot_journeys.append(Journey(
            journey_code=jcode,
            checkpoints=cps,
        ))

    out_floors = tmp_path / "frozen_quality_floors.json"
    res = evaluate_pilot_journeys(pilot_journeys, output_path=out_floors)
    assert res["gate"] == "G-3"
    assert res["gate_passed"] is True
    assert res["checkpoint_pass_rate"] == 1.0
    assert out_floors.exists()

    # Verify invalid count rejected
    with pytest.raises(ValueError, match="specifies exactly 10 pilot journeys"):
        evaluate_pilot_journeys(pilot_journeys[:5], output_path=out_floors)

    # Verify invalid journey code without PILOT- prefix rejected
    pilot_journeys[0].journey_code = "JRN-2026-0001"
    with pytest.raises(ValueError, match="must start with 'PILOT-'"):
        evaluate_pilot_journeys(pilot_journeys, output_path=out_floors)


def test_cli_scale_and_staging_commands(tmp_path: Path):
    """Verify CLI commands for scale, staging, truth, pilot, and split."""
    # 1. Scale record
    cal_dir = tmp_path / "cal"
    res_rec = runner.invoke(app, [
        "scale", "record",
        "--scale-id", "SCALE_TEST",
        "--load-g", "500.0",
        "-r", "500.1", "-r", "500.2", "-r", "500.1",
        "--output-dir", str(cal_dir),
    ])
    assert res_rec.exit_code == 0
    assert "Recorded 3 readings" in res_rec.stdout

    # Record 2 more loads to satisfy >= 3 loads requirement
    runner.invoke(app, [
        "scale", "record",
        "--scale-id", "SCALE_TEST",
        "--load-g", "100.0",
        "-r", "100.0", "-r", "100.0", "-r", "100.1",
        "--output-dir", str(cal_dir),
    ])
    runner.invoke(app, [
        "scale", "record",
        "--scale-id", "SCALE_TEST",
        "--load-g", "1000.0",
        "-r", "1000.1", "-r", "1000.2", "-r", "1000.0",
        "--output-dir", str(cal_dir),
    ])

    # 2. Scale fit
    scales_out = tmp_path / "scales.json"
    res_fit = runner.invoke(app, [
        "scale", "fit",
        "--scale-id", "SCALE_TEST",
        "--data-dir", str(cal_dir),
        "-o", str(scales_out),
    ])
    assert res_fit.exit_code == 0
    assert "fitted successfully (Gate G-4)" in res_fit.stdout

    # 3. Staging assign
    assign_dir = tmp_path / "assign"
    res_assign = runner.invoke(app, [
        "staging", "assign",
        "--n", "120",
        "--seed", "42",
        "--output-dir", str(assign_dir),
    ])
    assert res_assign.exit_code == 0
    assert "120 journeys across 8 scenario cells" in res_assign.stdout

    # 4. Staging log
    log_file = tmp_path / "staging_log.csv"
    res_log = runner.invoke(app, [
        "staging", "log",
        "-j", "JRN-2026-0001",
        "--cell", "intact",
        "-m", "Legitimate packaging",
        "-i", "none",
        "--stager-id", "STAGER_01",
        "--log-path", str(log_file),
    ])
    assert res_log.exit_code == 0
    assert "Staging record appended" in res_log.stdout

    # 5. Truth commit
    truth_manifest = tmp_path / "truth_manifest.json"
    res_commit = runner.invoke(app, [
        "truth", "commit",
        "--log-path", str(log_file),
        "--salt", "test-salt-secret",
        "-o", str(truth_manifest),
    ])
    assert res_commit.exit_code == 0
    assert "Gate G-2 Truth Commitment Manifest written" in res_commit.stdout

    # 6. Truth derive
    derived_truth = tmp_path / "derived_truth.json"
    res_derive = runner.invoke(app, [
        "truth", "derive",
        "--log-path", str(log_file),
        "-o", str(derived_truth),
    ])
    assert res_derive.exit_code == 0
    assert "Derived Ground Truth successfully" in res_derive.stdout

    # 7. Truth audit
    res_audit = runner.invoke(app, [
        "truth", "audit",
        "--sample", "1.0",
        "--log-path", str(log_file),
    ])
    assert res_audit.exit_code == 0
    assert "Independent Rule Audit Complete" in res_audit.stdout

    # 8. Split
    split_out = tmp_path / "split.json"
    res_split = runner.invoke(app, [
        "split",
        "-a", str(assign_dir / "staging_assignment_120.csv"),
        "-s", "42",
        "-o", str(split_out),
    ])
    assert res_split.exit_code == 0
    assert "Stratified split completed successfully" in res_split.stdout

    # 9. Pilot check
    floors_out = tmp_path / "frozen_floors.json"
    res_pilot = runner.invoke(app, [
        "pilot", "check",
        "-o", str(floors_out),
    ])
    assert res_pilot.exit_code == 0
    assert "Gate G-3 Status:     PASSED" in res_pilot.stdout
