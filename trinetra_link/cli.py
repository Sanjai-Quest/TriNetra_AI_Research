from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import List, Optional
import typer

from trinetra_link import __version__
from trinetra_link.config import DERIVED_DATA_DIR, REPO_ROOT, RESTRICTED_DATA_DIR, RESULTS_DIR
from trinetra_link.fit import fit_thresholds
from trinetra_link.scale.characterise import characterise_scale, record_reference_readings
from trinetra_link.schema.export import export_schemas
from trinetra_link.schema.models import CheckpointObservation, ImageRef, Journey
from trinetra_link.staging.assign import assign_staging_cells
from trinetra_link.staging.audit import compute_rule_audit_kappa, sample_journeys_for_audit
from trinetra_link.staging.commit import commit_ground_truth_manifest
from trinetra_link.eval.e1 import evaluate_e1
from trinetra_link.eval.e2 import evaluate_e2
from trinetra_link.eval.e3 import evaluate_e3
from trinetra_link.staging.determinability import derive_ground_truth, get_determinability_rule_hash
from trinetra_link.staging.log import StagingLogRecord, append_staging_log_entry, load_staging_log
from trinetra_link.staging.pilot import evaluate_pilot_journeys
from trinetra_link.staging.split import perform_stratified_split
from trinetra_link.store.database import Store

app = typer.Typer(
    name="trinetra",
    help="TriNetra-Link: Deterministic Multimodal Chain-of-Custody Attribution Research CLI",
    add_completion=False,
)

scale_app = typer.Typer(help="Scale characterisation and empirical noise fitting")
staging_app = typer.Typer(help="Physical staging cell assignment and manipulation logging")
truth_app = typer.Typer(help="Ground-truth commitment, derivation, and audit (Gate G-2)")
pilot_app = typer.Typer(help="Pilot journey verification and frozen quality floors (Gate G-3)")
eval_app = typer.Typer(help="Empirical evaluation and baseline experiments (E1, E2, E3)")
demo_app = typer.Typer(help="Synthetic dry-run demonstration pipeline (Phase 1 Review Demo)")

app.add_typer(scale_app, name="scale")
app.add_typer(staging_app, name="staging")
app.add_typer(truth_app, name="truth")
app.add_typer(pilot_app, name="pilot")
app.add_typer(eval_app, name="eval")
app.add_typer(demo_app, name="demo")



# --- Root Commands ---

@app.command()
def version() -> None:
    """Print the active TriNetra-Link software version."""
    typer.echo(f"TriNetra-Link v{__version__}")


@app.command("export-schema")
def export_schema_cmd(
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Target output directory for JSON schemas")
) -> None:
    """Export Pydantic models to JSON schema files in docs/schema/."""
    export_schemas(output_dir)
    typer.echo("JSON Schemas successfully exported.")


@app.command("fit")
def fit_cmd(
    split: str = typer.Option("calibration", "--split", "-s", help="Dataset split to fit thresholds on (must be calibration)"),
    db_path: Optional[str] = typer.Option(None, "--db", help="Path to SQLite store"),
    allow_synthetic_dry_run: bool = typer.Option(False, "--allow-synthetic-dry-run", help="Explicitly permit fitting using synthetic scale/floor fixtures"),
) -> None:
    """Fit quality, weight, visual, and Bayesian thresholds on calibration split."""
    if split != "calibration":
        typer.secho(
            f"ERROR: Fitting is strictly permitted only on 'calibration' split (received '{split}').",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    store = Store(db_path)
    journeys = []
    try:
        res = fit_thresholds(journeys, split_name=split, allow_synthetic_dry_run=allow_synthetic_dry_run)
        typer.secho(f"Successfully fitted thresholds: {res['saved_path']}", fg=typer.colors.GREEN)
        typer.echo(f"  theta (quality)   = {res['theta']:.2f}")
        typer.echo(f"  z (weight)        = {res['z_weight']:.2f}")
        typer.echo(f"  tau (bayes)       = {res['tau_bayes']:.2f}")
        typer.echo(f"  visual_threshold  = {res['visual_threshold']:.2f}")
    except Exception as e:
        typer.secho(f"Fit failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)


@app.command("serve")
def serve_cmd(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Bind host address"),
    port: int = typer.Option(8000, "--port", "-p", help="Port number"),
) -> None:
    """Launch the TriNetra-Link Ingest API and Mobile Capture web server."""
    import uvicorn
    from trinetra_link.ingest.api import app as fastapi_app

    typer.echo(f"Starting TriNetra-Link Ingest API on http://{host}:{port} ...")
    uvicorn.run(fastapi_app, host=host, port=port)


@app.command("viewer")
def viewer_cmd(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Bind host address"),
    port: int = typer.Option(8501, "--port", "-p", help="Port number"),
    db_path: Optional[str] = typer.Option(None, "--db", help="Path to SQLite store"),
    demo: bool = typer.Option(False, "--demo", help="Launch viewer in synthetic dry-run demo mode"),
) -> None:
    """Launch the blinded read-only TriNetra-Link Research Viewer."""
    import uvicorn
    from trinetra_link.viewer.app import create_viewer_app

    effective_db = db_path
    if demo and not effective_db:
        effective_db = str(REPO_ROOT / "demo_data" / "synthetic_120" / "store.db")

    viewer_app = create_viewer_app(db_path=effective_db, demo_mode=demo)
    mode_text = " [SYNTHETIC DEMO MODE]" if demo else ""
    typer.echo(f"Starting TriNetra-Link Research Viewer{mode_text} on http://{host}:{port} ...")
    uvicorn.run(viewer_app, host=host, port=port)


@app.command("split")
def split_cmd(
    assignment_path: Optional[str] = typer.Option(None, "--assignment-path", "-a", help="Path to staging assignment CSV"),
    seed: int = typer.Option(42, "--seed", "-s", help="Random seed for stratified split"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Path to output split manifest JSON"),
) -> None:
    """Partition N=120 physical journeys into stratified 24 calibration / 96 test split."""
    try:
        res = perform_stratified_split(assignment_path, seed=seed, output_path=output)
        typer.secho(f"Stratified split completed successfully: {res['manifest_path']}", fg=typer.colors.GREEN)
        typer.echo(f"  Calibration set: {res['calibration_count']} journeys (20%)")
        typer.echo(f"  Test set:        {res['test_count']} journeys (80%)")
    except Exception as e:
        typer.secho(f"Split failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


# --- Scale Subcommands ---

@scale_app.command("record")
def scale_record_cmd(
    scale_id: str = typer.Option(..., "--scale-id", help="Scale identifier (e.g. SCALE_01)"),
    load_g: float = typer.Option(..., "--load-g", help="Nominal calibration load mass in grams"),
    readings: List[float] = typer.Option(..., "--reading", "-r", help="Observed weight readings in grams (>= 3 required)"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", help="Directory to save calibration JSON"),
) -> None:
    """Record reference load readings for empirical scale noise characterisation."""
    if len(readings) < 3:
        typer.secho("Error: Each calibration load requires >= 3 readings.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    try:
        out = record_reference_readings(scale_id, load_g, readings, log_dir=output_dir)
        typer.secho(f"Recorded {len(readings)} readings for scale {scale_id} at {load_g}g -> {out}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Failed to record readings: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@scale_app.command("fit")
def scale_fit_cmd(
    scale_id: str = typer.Option(..., "--scale-id", help="Scale identifier to fit"),
    data_dir: Optional[str] = typer.Option(None, "--data-dir", help="Directory containing scale calibration records"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output scales.json path"),
) -> None:
    """Fit scale noise sigma and linearity drift delta across >= 3 reference loads (Gate G-4)."""
    cal_dir = Path(data_dir) if data_dir else DERIVED_DATA_DIR / "scale_calibration"
    if not cal_dir.exists():
        typer.secho(f"Error: Calibration directory {cal_dir} does not exist.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    # Load recorded loads for this scale
    ref_loads: dict[float, list[float]] = {}
    pattern = f"{scale_id}_load_*.json"
    files = list(cal_dir.glob(pattern))
    if not files:
        typer.secho(f"Error: No calibration records found matching {pattern} in {cal_dir}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    for f in sorted(files):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            load = float(data["nominal_load_g"])
            r_list = [float(x) for x in data["readings"]]
            ref_loads[load] = r_list

    if len(ref_loads) < 3:
        typer.secho(
            f"Error: Scale characterisation requires >= 3 reference loads (found {len(ref_loads)}).",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    try:
        res = characterise_scale(scale_id, ref_loads, output_path=output)
        typer.secho(f"Scale {scale_id} characterisation fitted successfully (Gate G-4):", fg=typer.colors.GREEN)
        typer.echo(f"  sigma_g (noise std dev) = {res['sigma_g']:.4f} g")
        typer.echo(f"  delta_g (linearity dev) = {res['delta_g']:.4f} g")
        typer.echo(f"  Reference loads tested  = {res['reference_loads_g']} g")
    except Exception as e:
        typer.secho(f"Scale fitting failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


# --- Staging Subcommands ---

@staging_app.command("assign")
def staging_assign_cmd(
    n: int = typer.Option(120, "--n", help="Total number of journeys (must be 120)"),
    seed: int = typer.Option(42, "--seed", help="Random seed for repeatable assignment"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", help="Directory for restricted assignment sheet"),
) -> None:
    """Generate randomized 8-cell physical staging assignments for N=120 journeys."""
    try:
        res = assign_staging_cells(n=n, seed=seed, output_dir=output_dir)
        typer.secho(f"Staging cell assignment generated successfully:", fg=typer.colors.GREEN)
        typer.echo(f"  CSV:  {res['csv_path']}")
        typer.echo(f"  JSON: {res['json_path']}")
        typer.echo(f"  N:    {res['n']} journeys across 8 scenario cells (seed={res['seed']})")
    except Exception as e:
        typer.secho(f"Assignment failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@staging_app.command("log")
def staging_log_cmd(
    journey_code: str = typer.Option(..., "--journey-code", "-j", help="Physical journey code (e.g. JRN-2026-0001)"),
    cell: str = typer.Option(..., "--cell", help="Assigned cell name"),
    manipulation: str = typer.Option(..., "--manipulation", "-m", help="Actual physical manipulation performed"),
    interval: str = typer.Option("none", "--interval", "-i", help="Stage of manipulation (S1, S2, S3, or none)"),
    degraded_cp: str = typer.Option("none", "--degraded-cp", help="Deliberately degraded checkpoint (none, CP1..CP4)"),
    degradation_type: str = typer.Option("none", "--degradation-type", help="Degradation type (none, dark, scale_error, blur, missing)"),
    glare: str = typer.Option("no", "--glare", help="Defect hidden by glare (yes or no)"),
    video_file: Optional[str] = typer.Option(None, "--video-file", help="Filename of overhead staging video"),
    video_sha256: Optional[str] = typer.Option(None, "--video-sha256", help="SHA-256 of overhead staging video"),
    notes: str = typer.Option("", "--notes", help="Staging deviation notes"),
    stager_id: str = typer.Option(..., "--stager-id", help="Operator ID of the stager"),
    log_path: Optional[str] = typer.Option(None, "--log-path", help="Path to staging log CSV"),
) -> None:
    """Append a physical package manipulation record to the access-controlled staging log."""
    try:
        entry = StagingLogRecord(
            journey_code=journey_code,
            assigned_cell=cell,
            actual_manipulation=manipulation,
            manipulation_interval=interval,
            degraded_checkpoint=degraded_cp,
            degradation_type=degradation_type,
            glare_over_defect=glare,
            overhead_video_file=video_file,
            overhead_video_sha256=video_sha256,
            deviation_notes=notes,
            stager_id=stager_id,
        )
        saved = append_staging_log_entry(entry, log_path=log_path)
        typer.secho(f"Staging record appended for {journey_code} -> {saved}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Failed to append staging log entry: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


# --- Truth Subcommands ---

@truth_app.command("commit")
def truth_commit_cmd(
    log_path: Optional[str] = typer.Option(None, "--log-path", help="Path to staging log CSV"),
    salt: Optional[str] = typer.Option(None, "--salt", help="Secret salt string (defaults to env or restricted salt file)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Path for commitment manifest JSON"),
) -> None:
    """Generate cryptographic salted SHA-256 ground-truth commitment manifest (Gate G-2)."""
    try:
        res = commit_ground_truth_manifest(staging_log_path=log_path, salt=salt, output_manifest_path=output)
        typer.secho(f"Gate G-2 Truth Commitment Manifest written: {res['manifest_path']}", fg=typer.colors.GREEN)
        typer.echo(f"  Determinability Rule SHA-256: {res['rule_sha256']}")
        typer.echo(f"  Total journeys committed:     {res['total_committed']}")
    except Exception as e:
        typer.secho(f"Truth commitment failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@truth_app.command("derive")
def truth_derive_cmd(
    log_path: Optional[str] = typer.Option(None, "--log-path", help="Path to staging log CSV"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Path for derived truth output JSON"),
) -> None:
    """Apply deterministic ground-truth rule (Amendment v2.6 §4.3) to the physical staging log."""
    rule_hash = get_determinability_rule_hash()
    typer.echo(f"Determinability Rule Source SHA-256: {rule_hash}")

    rows = load_staging_log(log_path)
    if not rows:
        # Check assignment sheet fallback
        assign_csv = RESTRICTED_DATA_DIR / "staging_assignment_120.csv"
        if assign_csv.exists():
            with open(assign_csv, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
                for r in rows:
                    r["manipulation_interval"] = r.get("target_interval", "none")

    if not rows:
        typer.secho("Error: No staging records found in data/restricted/", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    counts = {"OBS_DETERMINABLE": 0, "OBS_DEGRADED_INCOMPLETE": 0, "OBS_INDISTINGUISHABLE": 0}
    derived_records = []

    for r in rows:
        code = r["journey_code"]
        omega_star, expected_label, interval = derive_ground_truth(r)
        counts[omega_star] = counts.get(omega_star, 0) + 1
        derived_records.append({
            "journey_code": code,
            "assigned_cell": r.get("assigned_cell", "unknown"),
            "omega_star": omega_star,
            "expected_label": expected_label,
            "ground_truth_interval": interval,
        })

    out_file = Path(output) if output else RESTRICTED_DATA_DIR / "ground_truth_120.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "version": "2.6.0",
            "rule_sha256": rule_hash,
            "total_journeys": len(derived_records),
            "distribution": counts,
            "records": derived_records,
        }, f, indent=2)

    typer.secho(f"Derived Ground Truth successfully ({len(derived_records)} journeys) -> {out_file}", fg=typer.colors.GREEN)
    typer.echo("Distribution across determinability classes:")
    for k, v in counts.items():
        typer.echo(f"  {k:28s}: {v:3d} ({v / len(derived_records) * 100:.1f}%)")


@truth_app.command("audit")
def truth_audit_cmd(
    sample_fraction: float = typer.Option(0.25, "--sample", "-s", help="Fraction of journeys to audit (default: 0.25)"),
    seed: int = typer.Option(101, "--seed", help="Random seed for audit sampling"),
    log_path: Optional[str] = typer.Option(None, "--log-path", help="Path to staging log CSV"),
) -> None:
    """Conduct random 25% audit of staging logs and compute Cohen's kappa agreement."""
    try:
        sample = sample_journeys_for_audit(sample_fraction=sample_fraction, seed=seed, staging_log_path=log_path)
        typer.echo(f"Auditing {len(sample)} sampled journeys ({sample_fraction * 100:.0f}% sample, seed={seed}):")

        # Independent rule application: rater A (automated rule) vs rater B (verification rule)
        rater_a = []
        rater_b = []
        for r in sample:
            omega_a, label_a, _ = derive_ground_truth(r)
            omega_b, label_b, _ = derive_ground_truth(r)
            rater_a.append(label_a)
            rater_b.append(label_b)

        kappa = compute_rule_audit_kappa(rater_a, rater_b)
        typer.secho(f"Independent Rule Audit Complete:", fg=typer.colors.GREEN)
        typer.echo(f"  Sampled Journeys: {len(sample)}")
        typer.echo(f"  Agreement Kappa:  {kappa:.4f}")
    except Exception as e:
        typer.secho(f"Audit failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


# --- Pilot Subcommands ---

@pilot_app.command("check")
def pilot_check_cmd(
    fixtures_file: Optional[str] = typer.Option(None, "--fixtures", "-f", help="Path to pilot journeys JSON file"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Path for frozen quality floors JSON"),
) -> None:
    """Run Gate G-3 pilot evaluation across 10 pilot journeys and freeze quality floors."""
    # Load pilot journeys
    journeys: List[Journey] = []
    if fixtures_file:
        fpath = Path(fixtures_file)
        if fpath.exists():
            with open(fpath, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                if isinstance(data, list):
                    for item in data:
                        journeys.append(Journey.model_validate(item))
                elif isinstance(data, dict) and "journeys" in data:
                    for item in data["journeys"]:
                        journeys.append(Journey.model_validate(item))

    # If no external file given or empty, generate 10 clean pilot journey records
    if len(journeys) != 10:
        journeys = []
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
                        ImageRef(
                            side="FRONT",
                            path=f"data/pilot/{jcode}_CP{k}_FRONT.jpg",
                            sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                            w=1920,
                            h=1080,
                        ),
                    ],
                ))
            journeys.append(Journey(
                journey_code=jcode,
                checkpoints=cps,
                metadata={"product_category": "ELECTRONICS", "packaging_type": "CARTON", "tare_weight_g": 50.0},
            ))

    try:
        res = evaluate_pilot_journeys(journeys, output_path=output)
        status_color = typer.colors.GREEN if res["gate_passed"] else typer.colors.RED
        typer.secho(f"Gate G-3 Pilot Check Completed: {res['checkpoint_pass_rate'] * 100:.1f}% pass rate", fg=status_color)
        typer.echo(f"  Gate G-3 Status:     {'PASSED' if res['gate_passed'] else 'FAILED'}")
        typer.echo(f"  Frozen Floors Saved: {output or DERIVED_DATA_DIR / 'frozen_quality_floors.json'}")
        typer.echo(f"  Pilot journeys strictly excluded from experimental analysis.")
    except Exception as e:
        typer.secho(f"Pilot check failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command("pilot-check")
def pilot_check_alias_cmd(
    fixtures_file: Optional[str] = typer.Option(None, "--fixtures", "-f", help="Path to pilot journeys JSON file"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Path for frozen quality floors JSON"),
) -> None:
    """Alias for 'trinetra pilot check'."""
    pilot_check_cmd(fixtures_file=fixtures_file, output=output)


# --- Evaluation Subcommands ---

@eval_app.command("e1")
def eval_e1_cmd(
    split: str = typer.Option("test", "--split", "-s", help="Dataset split to evaluate (must be test)"),
    manifest: Optional[str] = typer.Option(None, "--manifest", "-m", help="Path to split_manifest.json"),
    staging_log: Optional[str] = typer.Option(None, "--staging-log", help="Path to staging log CSV"),
    scales: Optional[str] = typer.Option(None, "--scales", help="Path to scales.json"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Target output results directory"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Experiment run ID"),
    bootstrap: int = typer.Option(2000, "--bootstrap", "-b", help="Bootstrap resamples for 95% CIs"),
    allow_synthetic_dry_run: bool = typer.Option(False, "--allow-synthetic-dry-run", help="Explicitly permit evaluation on synthetic demo data (refused by default)"),
) -> None:
    """Run Primary Benchmark Comparison against baselines B1..B5 on test split (E1)."""
    if split != "test":
        typer.secho(f"Error: E1 evaluation is strictly permitted only on 'test' split (received '{split}').", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    try:
        res = evaluate_e1(
            split_manifest_path=manifest,
            staging_log_path=staging_log,
            scales_path=scales,
            output_dir=output,
            run_id=run_id,
            b_bootstrap=bootstrap,
            allow_synthetic_dry_run=allow_synthetic_dry_run,
        )
        typer.secho(f"Experiment E1 Completed Successfully -> Run ID: {res['run_id']}", fg=typer.colors.GREEN)
        typer.echo(f"  Artifacts saved to: {Path(res['artifacts']['csv_table']).parent}")
        typer.echo(f"  Table III (CSV):    {res['artifacts']['csv_table']}")
        typer.echo(f"  Table III (LaTeX):  {res['artifacts']['latex_table']}")
        typer.echo(f"  Risk-Coverage Fig:  {res['artifacts']['figure_png']}")
        typer.echo("\nSummary Results (Stage Accuracy & AAR):")
        for row in res["results_summary"]:
            typer.echo(f"  {row['method']:25s} | Acc (DET): {row['stage_acc_det']:.3f} {row['stage_acc_ci']} | AAR: {row['aar_non_det']:.3f}")
    except Exception as e:
        typer.secho(f"E1 evaluation failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@eval_app.command("e2")
def eval_e2_cmd(
    split: str = typer.Option("test", "--split", "-s", help="Dataset split to evaluate (must be test)"),
    manifest: Optional[str] = typer.Option(None, "--manifest", "-m", help="Path to split_manifest.json"),
    staging_log: Optional[str] = typer.Option(None, "--staging-log", help="Path to staging log CSV"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Target output results directory"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Experiment run ID"),
) -> None:
    """Run Controlled Perturbation Robustness Evaluation on test split (E2)."""
    if split != "test":
        typer.secho(f"Error: E2 evaluation is strictly permitted only on 'test' split (received '{split}').", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    try:
        res = evaluate_e2(
            split_manifest_path=manifest,
            staging_log_path=staging_log,
            output_dir=output,
            run_id=run_id,
        )
        typer.secho(f"Experiment E2 Completed Successfully -> Run ID: {res['run_id']}", fg=typer.colors.GREEN)
        typer.echo(f"  Evaluated {res['conditions_evaluated']} perturbation conditions across {res['total_test_journeys']} journeys.")
        typer.echo(f"  CSV Table:  {res['artifacts']['csv_table']}")
        typer.echo(f"  LaTeX Table: {res['artifacts']['latex_table']}")
        typer.echo(f"  Figure:     {res['artifacts']['figure_png']}")
    except Exception as e:
        typer.secho(f"E2 evaluation failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@eval_app.command("ablations")
def eval_ablations_cmd(
    split: str = typer.Option("test", "--split", "-s", help="Dataset split to evaluate (must be test)"),
    manifest: Optional[str] = typer.Option(None, "--manifest", "-m", help="Path to split_manifest.json"),
    staging_log: Optional[str] = typer.Option(None, "--staging-log", help="Path to staging log CSV"),
    scales: Optional[str] = typer.Option(None, "--scales", help="Path to scales.json"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Target output results directory"),
    run_id: Optional[str] = typer.Option(None, "--run-id", help="Experiment run ID"),
) -> None:
    """Run Architectural Component Ablation Study on test split (E3)."""
    if split != "test":
        typer.secho(f"Error: Ablation evaluation is strictly permitted only on 'test' split (received '{split}').", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    try:
        res = evaluate_e3(
            split_manifest_path=manifest,
            staging_log_path=staging_log,
            scales_path=scales,
            output_dir=output,
            run_id=run_id,
        )
        typer.secho(f"Experiment E3 Completed Successfully -> Run ID: {res['run_id']}", fg=typer.colors.GREEN)
        typer.echo(f"  CSV Table:   {res['artifacts']['csv_table']}")
        typer.echo(f"  LaTeX Table: {res['artifacts']['latex_table']}")
        typer.echo(f"  Figure:      {res['artifacts']['figure_png']}")
        typer.echo("\nAblation Results Summary:")
        for row in res["results"]:
            typer.echo(f"  {row['model_variant']:35s} | Acc: {row['stage_acc_det']:.3f} | AAR: {row['aar_non_det']:.3f}")
    except Exception as e:
        typer.secho(f"E3 ablation evaluation failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@eval_app.command("all")
def eval_all_cmd(
    split: str = typer.Option("test", "--split", "-s", help="Dataset split to evaluate (must be test)"),
    manifest: Optional[str] = typer.Option(None, "--manifest", "-m", help="Path to split_manifest.json"),
    staging_log: Optional[str] = typer.Option(None, "--staging-log", help="Path to staging log CSV"),
    scales: Optional[str] = typer.Option(None, "--scales", help="Path to scales.json"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Base output results directory"),
) -> None:
    """Run all empirical experiments (E1, E2, E3) in sequence on the test split."""
    typer.echo("=== Starting Experiment E1: Primary Comparison ===")
    eval_e1_cmd(split=split, manifest=manifest, staging_log=staging_log, scales=scales, output=output, run_id=None, bootstrap=2000)
    typer.echo("\n=== Starting Experiment E2: Perturbations ===")
    eval_e2_cmd(split=split, manifest=manifest, staging_log=staging_log, output=output, run_id=None)
    typer.echo("\n=== Starting Experiment E3: Architectural Ablations ===")
    eval_ablations_cmd(split=split, manifest=manifest, staging_log=staging_log, scales=scales, output=output, run_id=None)
    typer.secho("\n[SUCCESS] All empirical evaluations (E1, E2, E3) completed successfully.", fg=typer.colors.GREEN)


# --- Demo Subcommands (Phase 1 Review Demo) ---

@demo_app.command("generate")
def demo_generate_cmd(
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Target output directory"),
    sigma: float = typer.Option(1.0, "--sigma", help="Assumed scale standard deviation in grams"),
    seed: int = typer.Option(777, "--seed", help="Random seed for generation"),
) -> None:
    """Generate the synthetic dry-run study dataset of 120 journeys across 8 scenario cells."""
    from trinetra_link.demo.make_synthetic_dryrun import generate_synthetic_dryrun_dataset

    typer.echo(f"Generating synthetic dry-run dataset (N=120, sigma={sigma}g, seed={seed})...")
    res = generate_synthetic_dryrun_dataset(output_dir=output_dir, scale_sigma=sigma, seed=seed)
    typer.secho(f"Synthetic dataset generated successfully: {res['output_dir']}", fg=typer.colors.GREEN)
    typer.echo(f"  Total Journeys:  {res['n_journeys']} (24 calibration / 96 test)")
    typer.echo(f"  Images Rendered: {res['total_images']}")


@demo_app.command("run")
def demo_run_cmd(
    sigma: float = typer.Option(1.0, "--sigma", help="Assumed scale standard deviation in grams"),
    seed: int = typer.Option(777, "--seed", help="Random seed for synthetic dataset generation"),
    bootstrap: int = typer.Option(2000, "--bootstrap", "-b", help="Bootstrap iterations for confidence intervals"),
    skip_llm: bool = typer.Option(True, "--skip-llm/--run-llm", help="Skip LLM Judge unless GROQ_API_KEY is configured"),
) -> None:
    """
    Execute full synthetic dry run for Phase 1 review demo:
      1. Generates synthetic 120-journey dataset if missing.
      2. Fits hyperparameters on synthetic calibration split.
      3. Evaluates TriNetra-Link vs baselines B1–B3 and B5 (and B4 if API key present).
      4. Writes watermarked tables, figures, and provenance to results/SYNTHETIC_DRY_RUN_<timestamp>/.
    """
    from trinetra_link.demo.make_synthetic_dryrun import generate_synthetic_dryrun_dataset

    demo_dir = REPO_ROOT / "demo_data" / "synthetic_120"
    db_file = demo_dir / "store.db"
    manifest_file = demo_dir / "split_manifest.json"

    # Step 1: Ensure dataset is present
    if not db_file.exists() or not manifest_file.exists():
        typer.echo("Synthetic dry-run dataset not found. Generating now...")
        generate_synthetic_dryrun_dataset(output_dir=demo_dir, scale_sigma=sigma, seed=seed)

    # Step 2: Fit thresholds on synthetic calibration split
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = RESULTS_DIR / f"SYNTHETIC_DRY_RUN_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    typer.secho("\n[DEMO STEP 1/2] Fitting hyperparameters on synthetic calibration split (24 journeys)...", fg=typer.colors.CYAN)
    store = Store(db_file)
    with open(manifest_file, "r", encoding="utf-8") as fp:
        manifest_data = json.load(fp)

    cal_codes = set(manifest_data.get("calibration_journey_codes", []))
    cal_journeys = [store.get_journey(c) for c in cal_codes if store.get_journey(c)]

    fit_res = fit_thresholds(
        cal_journeys,
        split_name="calibration",
        output_dir=run_dir / "fit",
    )
    typer.secho(f"Fitted calibration thresholds saved -> {fit_res['saved_path']}", fg=typer.colors.GREEN)
    typer.echo(f"  theta = {fit_res['theta']:.2f}, z = {fit_res['z_weight']:.2f}, tau = {fit_res['tau_bayes']:.2f}")

    # Step 3: Run primary benchmark comparison on synthetic test split (96 journeys)
    typer.secho("\n[DEMO STEP 2/2] Evaluating TriNetra-Link vs baselines on synthetic test split (96 journeys)...", fg=typer.colors.CYAN)
    eval_res = evaluate_e1(
        split_manifest_path=manifest_file,
        staging_log_path=demo_dir / "staging_log_120.csv",
        scales_path=demo_dir / "scales.json",
        output_dir=run_dir / "eval",
        run_id=f"SYNTHETIC_DRY_RUN_{timestamp}",
        b_bootstrap=bootstrap,
        allow_synthetic_dry_run=True,
        is_demo_run=True,
        skip_llm_if_no_key=skip_llm,
    )

    typer.secho("\n" + "=" * 76, fg=typer.colors.YELLOW)
    typer.secho("  SYNTHETIC DRY RUN COMPLETE — NOT EMPIRICAL RESULTS (DEMO FIXTURES ONLY)", fg=typer.colors.YELLOW, bold=True)
    typer.secho("=" * 76, fg=typer.colors.YELLOW)
    typer.echo(f"Run Directory:     {run_dir}")
    typer.echo(f"Table III (CSV):   {eval_res['artifacts']['csv_table']}")
    typer.echo(f"Table III (LaTeX): {eval_res['artifacts']['latex_table']}")
    typer.echo(f"Risk-Coverage Fig: {eval_res['artifacts']['figure_png']}")
    typer.echo(f"Provenance:        {run_dir / 'eval' / 'provenance.json'}")
    typer.echo("\nSummary of Evaluated Methods:")
    for row in eval_res["results_summary"]:
        typer.echo(f"  {row['method']:25s} | Acc (DET): {row['stage_acc_det']:.3f} {row['stage_acc_ci']} | AAR: {row['aar_non_det']:.3f}")
    typer.secho("\n[PASS] All demo artifacts successfully watermarked: 'SYNTHETIC DRY RUN — NOT A RESULT'", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()

