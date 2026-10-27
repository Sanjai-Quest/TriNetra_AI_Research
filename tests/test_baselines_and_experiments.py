from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import pytest
from typer.testing import CliRunner

from trinetra_link.baselines.b1_cp4 import predict_b1_cp4
from trinetra_link.baselines.b2_endpoints import predict_b2_endpoints
from trinetra_link.baselines.b3_unlinked import predict_b3_unlinked
from trinetra_link.baselines.b4_llm_judge import predict_b4_llm_judge
from trinetra_link.baselines.b5_v3_rules import predict_b5_v3_rules
from trinetra_link.cli import app
from trinetra_link.eval.e1 import evaluate_e1, generate_benchmark_journey_from_staging
from trinetra_link.eval.e2 import evaluate_e2, perturb_drop_checkpoint, perturb_scale_drift
from trinetra_link.eval.e3 import evaluate_e3
from trinetra_link.eval.metrics import (
    bootstrap_metric_ci,
    compute_abstention_metrics,
    compute_macro_f1,
    compute_risk_coverage_curve,
    compute_stage_accuracy,
    exact_mcnemar_test,
)
from trinetra_link.eval.pipeline import canonicalize_label, predict_trinetra_link
from trinetra_link.schema.models import CheckpointObservation, ImageRef, Journey
from trinetra_link.staging.assign import assign_staging_cells
from trinetra_link.staging.split import perform_stratified_split

runner = CliRunner()


def make_test_journey(
    code: str = "JRN-TEST-001",
    weights_per_cp: Optional[list[list[float]]] = None,
    seal_per_cp: Optional[list[str]] = None,
    scale_statuses: Optional[list[str]] = None,
    serials_per_cp: Optional[list[str]] = None,
) -> Journey:
    w_list = weights_per_cp or [[500.0, 500.0, 500.0] for _ in range(4)]
    s_list = seal_per_cp or ["SEAL-ORIG" for _ in range(4)]
    st_list = scale_statuses or ["OK" for _ in range(4)]
    sn_list = serials_per_cp or ["SN-100" for _ in range(4)]

    cps = []
    for k in (1, 2, 3, 4):
        cps.append(CheckpointObservation(
            journey_code=code,
            cp_index=k,
            ts_utc=datetime.now(timezone.utc),
            device_id=f"DEV-{k}",
            operator_id=f"OP-{k}",
            weights_g=w_list[k - 1],
            scale_id="SCALE-STD",
            scale_status=st_list[k - 1],
            seal_qr=s_list[k - 1],
            serial=sn_list[k - 1],
            imei="IMEI-100",
            images=[
                ImageRef(side="TOP", path=f"mock_{k}.jpg", sha256="fake", w=800, h=600)
            ],
        ))
    return Journey(journey_code=code, checkpoints=cps)


def test_baseline_b1_cp4():
    """Verify B1 CP4-only terminal classification."""
    clean_j = make_test_journey()
    res_clean = predict_b1_cp4(clean_j)
    assert res_clean.label == "ATTR_CONFIRMED_LEGITIMATE"

    # Terminal weight anomaly at CP4
    tampered_j = make_test_journey(
        weights_per_cp=[[500.0]*3, [500.0]*3, [500.0]*3, [450.0]*3]
    )
    res_tamp = predict_b1_cp4(tampered_j)
    assert res_tamp.label == "ATTR_STAGE_REVERSE_TRANSIT"


def test_baseline_b2_endpoints():
    """Verify B2 CP1+CP4 endpoint comparison."""
    clean_j = make_test_journey()
    assert predict_b2_endpoints(clean_j).label == "ATTR_CONFIRMED_LEGITIMATE"

    # Endpoints differ (CP4 lighter)
    tampered_j = make_test_journey(
        weights_per_cp=[[500.0]*3, [500.0]*3, [500.0]*3, [480.0]*3]
    )
    assert predict_b2_endpoints(tampered_j).label == "ATTR_STAGE_REVERSE_TRANSIT"


def test_baseline_b3_unlinked():
    """Verify B3 first detection = origin attribution."""
    # Anomaly at CP2 -> S1
    j_s1 = make_test_journey(
        weights_per_cp=[[500.0]*3, [470.0]*3, [470.0]*3, [470.0]*3]
    )
    assert predict_b3_unlinked(j_s1).label == "ATTR_STAGE_FORWARD_TRANSIT"

    # Anomaly at CP3 -> S2
    j_s2 = make_test_journey(
        weights_per_cp=[[500.0]*3, [500.0]*3, [470.0]*3, [470.0]*3]
    )
    assert predict_b3_unlinked(j_s2).label == "ATTR_STAGE_CONSUMER_CUSTODY"

    # Anomaly at CP4 -> S3
    j_s3 = make_test_journey(
        weights_per_cp=[[500.0]*3, [500.0]*3, [500.0]*3, [470.0]*3]
    )
    assert predict_b3_unlinked(j_s3).label == "ATTR_STAGE_REVERSE_TRANSIT"


def test_baseline_b4_llm_judge(monkeypatch):
    """Verify B4 skips / refuses when GROQ_API_KEY is missing, and queries when key is present."""
    from unittest.mock import patch
    clean_j = make_test_journey()

    # When key is missing -> raises RuntimeError
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GROQ_API_KEY is missing"):
        predict_b4_llm_judge(clean_j)

    # When key is provided -> queries API and returns consensus
    with patch("trinetra_link.baselines.b4_llm_judge.query_groq_llm", return_value={"label": "ATTR_CONFIRMED_LEGITIMATE", "confidence": 0.95, "rationale": "mock"}):
        res = predict_b4_llm_judge(clean_j, groq_api_key="gsk_mock_test_key")
        assert res.label == "ATTR_CONFIRMED_LEGITIMATE"


def test_baseline_b5_v3_rules():
    """Verify B5 ported V3 rules (uses only serial/IMEI/custody without weight or images)."""
    clean_j = make_test_journey()
    assert predict_b5_v3_rules(clean_j).label == "ATTR_CONFIRMED_LEGITIMATE"

    # Serial mismatch at CP2 -> S1 (ATTR_STAGE_FORWARD_TRANSIT)
    serial_j = make_test_journey(serials_per_cp=["SN-100", "SN-TAMPER", "SN-TAMPER", "SN-TAMPER"])
    assert predict_b5_v3_rules(serial_j).label == "ATTR_STAGE_FORWARD_TRANSIT"


def test_metrics_computation():
    """Verify evaluation metric calculators."""
    preds = ["ATTR_STAGE_FORWARD_TRANSIT", "ATTR_STAGE_CONSUMER_CUSTODY", "ATTR_ABSTAIN_DEGRADED", "ATTR_STAGE_FORWARD_TRANSIT"]
    gts   = ["ATTR_STAGE_FORWARD_TRANSIT", "ATTR_STAGE_CONSUMER_CUSTODY", "ATTR_ABSTAIN_DEGRADED", "ATTR_STAGE_REVERSE_TRANSIT"]
    omegas = ["OBS_DETERMINABLE", "OBS_DETERMINABLE", "OBS_DEGRADED_INCOMPLETE", "OBS_DETERMINABLE"]

    acc, corr, tot = compute_stage_accuracy(preds, gts, omegas)
    assert tot == 3
    assert corr == 2
    assert acc == round(2 / 3, 4)

    f1 = compute_macro_f1(preds, gts, omegas)
    assert 0.0 < f1 <= 1.0

    abs_m = compute_abstention_metrics(preds, gts, omegas)
    assert abs_m["aar"] == 1.0  # 1 non-det correctly abstained
    assert abs_m["ubr"] == 0.0
    assert abs_m["uar"] == 0.0

    covs, risks, aurc = compute_risk_coverage_curve(preds, [0.95, 0.90, 0.85, 0.70], gts, omegas)
    assert 0.0 <= aurc <= 1.0

    # McNemar test
    preds_b = ["ATTR_STAGE_FORWARD_TRANSIT", "ATTR_STAGE_FORWARD_TRANSIT", "ATTR_ABSTAIN_DEGRADED", "ATTR_STAGE_REVERSE_TRANSIT"]
    b_disc, c_disc, p_val = exact_mcnemar_test(preds, preds_b, gts)
    assert p_val > 0.0

    # Bootstrap CI
    def acc_fn(p, g, o):
        a, _, _ = compute_stage_accuracy(p, g, o)
        return a

    pt, low, high = bootstrap_metric_ci(acc_fn, preds, gts, omegas, b=100)
    assert low <= pt <= high


def test_experiments_e1_e2_e3_integration(tmp_path: Path):
    """Verify full end-to-end execution of E1, E2, E3 experiments and table generation."""
    # 1. Setup restricted assignment and split manifest
    res_assign = assign_staging_cells(n=120, seed=42, output_dir=tmp_path / "restricted")
    split_manifest = tmp_path / "split_manifest.json"
    perform_stratified_split(assignments_csv_path=res_assign["csv_path"], seed=42, output_path=split_manifest)

    # 2. Run E1
    e1_dir = tmp_path / "results_e1"
    e1_res = evaluate_e1(
        split_manifest_path=split_manifest,
        staging_log_path=res_assign["csv_path"],
        output_dir=e1_dir,
        b_bootstrap=100,  # Fast bootstrap for test suite
    )
    expected_methods = 7 if os.environ.get("GROQ_API_KEY") else 6
    assert len(e1_res["results_summary"]) == expected_methods
    assert Path(e1_res["artifacts"]["csv_table"]).exists()
    assert Path(e1_res["artifacts"]["latex_table"]).exists()
    assert Path(e1_res["artifacts"]["figure_png"]).exists()
    assert Path(e1_res["artifacts"]["figure_pdf"]).exists()

    # 3. Run E2
    e2_dir = tmp_path / "results_e2"
    e2_res = evaluate_e2(
        split_manifest_path=split_manifest,
        staging_log_path=res_assign["csv_path"],
        output_dir=e2_dir,
    )
    assert e2_res["conditions_evaluated"] >= 10
    assert Path(e2_res["artifacts"]["csv_table"]).exists()
    assert Path(e2_res["artifacts"]["figure_png"]).exists()

    # 4. Run E3
    e3_dir = tmp_path / "results_e3"
    e3_res = evaluate_e3(
        split_manifest_path=split_manifest,
        staging_log_path=res_assign["csv_path"],
        output_dir=e3_dir,
    )
    assert len(e3_res["results"]) == 5
    assert Path(e3_res["artifacts"]["csv_table"]).exists()
    assert Path(e3_res["artifacts"]["figure_png"]).exists()


def test_cli_eval_commands(tmp_path: Path):
    """Verify CLI commands for trinetra eval e1, e2, ablations."""
    res_assign = assign_staging_cells(n=120, seed=42, output_dir=tmp_path / "restricted")
    split_manifest = tmp_path / "split_manifest.json"
    perform_stratified_split(assignments_csv_path=res_assign["csv_path"], seed=42, output_path=split_manifest)

    # Test eval e1
    res_e1 = runner.invoke(app, [
        "eval", "e1",
        "--split", "test",
        "-m", str(split_manifest),
        "--staging-log", str(res_assign["csv_path"]),
        "-o", str(tmp_path / "cli_e1"),
        "-b", "50",
    ])
    assert res_e1.exit_code == 0, f"res_e1 failed: {res_e1.output}"
    assert "Experiment E1 Completed Successfully" in res_e1.stdout

    # Test eval e2
    res_e2 = runner.invoke(app, [
        "eval", "e2",
        "--split", "test",
        "-m", str(split_manifest),
        "--staging-log", str(res_assign["csv_path"]),
        "-o", str(tmp_path / "cli_e2"),
    ])
    assert res_e2.exit_code == 0, f"res_e2 failed: {res_e2.output}"
    assert "Experiment E2 Completed Successfully" in res_e2.stdout

    # Test eval ablations
    res_e3 = runner.invoke(app, [
        "eval", "ablations",
        "--split", "test",
        "-m", str(split_manifest),
        "--staging-log", str(res_assign["csv_path"]),
        "-o", str(tmp_path / "cli_e3"),
    ])
    assert res_e3.exit_code == 0, f"res_e3 failed: {res_e3.output}"
    assert "Experiment E3 Completed Successfully" in res_e3.stdout
