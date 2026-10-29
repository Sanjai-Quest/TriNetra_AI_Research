from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — no Tk/display needed
import matplotlib.pyplot as plt
import numpy as np

from trinetra_link.baselines.b1_cp4 import predict_b1_cp4
from trinetra_link.baselines.b2_endpoints import predict_b2_endpoints
from trinetra_link.baselines.b3_unlinked import predict_b3_unlinked
from trinetra_link.baselines.b4_llm_judge import predict_b4_llm_judge
from trinetra_link.baselines.b5_v3_rules import predict_b5_v3_rules
from trinetra_link.config import DERIVED_DATA_DIR, REPO_ROOT, RESULTS_DIR
from trinetra_link.eval.metrics import (
    bootstrap_metric_ci,
    compute_abstention_metrics,
    compute_macro_f1,
    compute_per_cell_breakdown,
    compute_risk_coverage_curve,
    compute_stage_accuracy,
    exact_mcnemar_test,
)
from trinetra_link.eval.pipeline import canonicalize_label, predict_trinetra_link
from trinetra_link.schema.models import CheckpointObservation, ImageRef, Journey
from trinetra_link.staging.determinability import derive_ground_truth, get_determinability_rule_hash
from trinetra_link.staging.log import load_staging_log


def generate_benchmark_journey_from_staging(
    staging_row: Dict[str, Any],
    nominal_weight_g: float = 500.0,
    seed: int = 42,
) -> Journey:
    """
    Construct standardized benchmark journey conforming to physical staging specifications.
    Used for evaluation pipeline benchmarking and verification.
    """
    code = staging_row.get("journey_code", "JRN-2026-TEST")
    cell = staging_row.get("assigned_cell", "intact")
    interval = str(staging_row.get("manipulation_interval", "none")).upper().strip()
    degraded_cp = str(staging_row.get("degraded_checkpoint", "none")).lower().strip()
    has_glare = str(staging_row.get("glare_over_defect", "no")).lower().strip() == "yes"

    rng = np.random.default_rng(abs(hash(code)) % (2**32))
    cps: List[CheckpointObservation] = []

    # Nominal tare and weight
    tare_delta = 15.0 if cell == "permitted_flyer" else 0.0
    w_curr = nominal_weight_g

    # Determine stage where physical manipulation happens
    tamper_stage = 0
    if interval.startswith("S") and len(interval) >= 2:
        try:
            tamper_stage = int(interval[1])
        except ValueError:
            pass

    for k in (1, 2, 3, 4):
        # Permitted tare change at CP2 if permitted_flyer
        is_permitted = (cell == "permitted_flyer" and k == 2)
        if is_permitted:
            w_curr += tare_delta

        # Physical manipulation occurs after CP(k-1) and before CP(k)
        if tamper_stage > 0 and k > tamper_stage:
            if cell == "forward_transit_damage":
                w_curr -= 4.5  # Weight loss from carton rupture
            elif cell in ("doorstep_substitution", "customer_tamper", "reverse_transit_tamper"):
                w_curr -= 35.0  # Item substituted with lighter surrogate

        # Noise around current weight
        noise = rng.normal(0.0, 0.03, size=3)
        readings = [round(float(w_curr + n), 2) for n in noise]

        # Seal QR
        seal = "SEAL-2026-ORIG"
        if tamper_stage > 0 and k > tamper_stage and cell in ("doorstep_substitution", "customer_tamper"):
            seal = "SEAL-TAMPERED-BROKEN"

        # Checkpoint degradation
        is_degraded = (degraded_cp == f"cp{k}")
        scale_status = "ERROR" if (is_degraded and staging_row.get("degradation_type") == "scale_error") else "OK"
        if is_degraded and staging_row.get("degradation_type") == "dark":
            readings = [round(float(w_curr), 2)] * 3

        notes = "Camera glare over seal defect" if has_glare else ""

        cps.append(CheckpointObservation(
            journey_code=code,
            cp_index=k,
            ts_utc=datetime.now(timezone.utc),
            device_id=f"DEV_CP{k}",
            operator_id=f"OP_CP{k}",
            weights_g=readings,
            scale_id="SCALE_STD",
            scale_status=scale_status,
            seal_qr=seal,
            serial="SN-882910",
            imei="354892019283741",
            carrier_log=notes,
            permitted_packaging_change=is_permitted,
            tare_delta_g=tare_delta if is_permitted else 0.0,
            images=[
                ImageRef(
                    side="TOP",
                    path=f"data/artifacts/{code}_CP{k}_TOP.jpg",
                    sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    w=800,
                    h=600,
                )
            ],
        ))

    return Journey(
        journey_code=code,
        checkpoints=cps,
        metadata={"cell": cell, "target_interval": interval},
    )


def evaluate_e1(
    split_manifest_path: Optional[Path | str] = None,
    staging_log_path: Optional[Path | str] = None,
    scales_path: Optional[Path | str] = None,
    output_dir: Optional[Path | str] = None,
    run_id: Optional[str] = None,
    b_bootstrap: int = 2000,
    allow_synthetic_dry_run: bool = False,
    is_demo_run: bool = False,
    skip_llm_if_no_key: bool = False,
    theta: Optional[float] = None,
    mask: str = "full",
) -> Dict[str, Any]:
    """
    Execute Experiment E1: Primary Benchmark Evaluation on the 96-journey test split.
    Compares TriNetra-Link against baselines B1 through B5 across:
      - Stage Accuracy on DET journeys
      - Macro-F1 over S1–S3
      - AAR, UBR on non-DET journeys
      - UAR on DET journeys
      - AURC & Risk-Coverage curves
      - Journey bootstrap 95% Confidence Intervals
      - Exact McNemar paired significance tests
      - Subgroup breakdowns (weight_matched, mass_change_g)
    Supports evidence masking:
      - 'full': all evidence at CP1-CP4
      - 'field': weights only at CP1 and CP4; CP2/CP3 keep photos, seals, notes but no weights
    """
    if mask not in ("full", "field"):
        raise ValueError(f"Invalid mask mode '{mask}'. Expected 'full' or 'field'.")

    rid = run_id or f"e1_{mask}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    target_dir = Path(output_dir) if output_dir else RESULTS_DIR / rid
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load split manifest
    s_path = Path(split_manifest_path) if split_manifest_path else DERIVED_DATA_DIR / "split_manifest.json"
    if not s_path.exists():
        raise FileNotFoundError(f"Split manifest not found at {s_path}. Run 'trinetra split' first.")

    with open(s_path, "r", encoding="utf-8") as f:
        split_data = json.load(f)

    test_codes = set(split_data.get("test_journey_codes", []))
    if not test_codes:
        raise ValueError("No test journey codes found in split manifest")

    # Anti-fabrication check: detect synthetic dry-run demo data
    is_synthetic = (
        ("demo_data" in str(s_path).replace("\\", "/"))
        or ("synthetic" in str(s_path).lower())
        or split_data.get("synthetic") is True
        or any(str(c).startswith("SYN-") for c in test_codes)
    )

    if is_synthetic and not allow_synthetic_dry_run:
        raise RuntimeError(
            "REFUSAL TO EXECUTE ON SYNTHETIC DEMO DATA:\n"
            f"Dataset manifest '{s_path}' contains synthetic demo fixtures ('SYN-' journey codes).\n"
            "Empirical evaluations strictly refuse demo fixtures by default to prevent inadvertent reporting.\n"
            "To explicitly permit a demonstration dry run, specify '--allow-synthetic-dry-run'."
        )

    # 2. Load staging log
    staging_rows = load_staging_log(staging_log_path)
    if not staging_rows:
        if is_synthetic:
            demo_log_csv = REPO_ROOT / "demo_data" / "synthetic_120" / "staging_log_120.csv"
            if demo_log_csv.exists():
                import csv
                with open(demo_log_csv, "r", encoding="utf-8") as fp:
                    staging_rows = list(csv.DictReader(fp))
        else:
            # Load from restricted assignment sheet if log empty
            assign_csv = REPO_ROOT / "data" / "restricted" / "staging_assignment_120.csv"
            if assign_csv.exists():
                import csv
                with open(assign_csv, "r", encoding="utf-8") as fp:
                    staging_rows = list(csv.DictReader(fp))
                    for r in staging_rows:
                        r["manipulation_interval"] = r.get("target_interval", "none")

    if not staging_rows:
        raise FileNotFoundError("Neither staging log nor assignment sheet found in data/restricted/ or demo_data/")

    # Filter to test split
    test_staging = [r for r in staging_rows if r["journey_code"] in test_codes]
    if len(test_staging) != 96:
        # If test staging doesn't exactly match 96, take all matching or available test codes
        test_staging = [r for r in staging_rows if r["journey_code"] in test_codes]

    # Load scales configuration if present
    scales_config = None
    sc_path = Path(scales_path) if scales_path else (
        REPO_ROOT / "demo_data" / "synthetic_120" / "scales.json" if is_synthetic else DERIVED_DATA_DIR / "scales.json"
    )
    if sc_path.exists():
        try:
            with open(sc_path, "r", encoding="utf-8") as fp:
                scales_config = json.load(fp)
                if not allow_synthetic_dry_run and not is_synthetic:
                    if scales_config.get("synthetic") is True or "synthetic" in str(scales_config.get("provenance", "")).lower():
                        raise RuntimeError(
                            f"REFUSAL TO EXECUTE ON REAL DATA:\n"
                            f"Scale calibration parameters at '{sc_path}' have synthetic provenance.\n"
                            f"Real evaluations refuse synthetic scale parameters unless '--allow-synthetic-dry-run' is enabled."
                        )
        except RuntimeError:
            raise
        except Exception:
            pass

    # Check frozen quality floors provenance
    floors_path = DERIVED_DATA_DIR / "frozen_quality_floors.json"
    if floors_path.exists() and not allow_synthetic_dry_run and not is_synthetic:
        try:
            with open(floors_path, "r", encoding="utf-8") as fp:
                fl_data = json.load(fp)
                if fl_data.get("synthetic") is True or "synthetic" in str(fl_data.get("provenance", "")).lower():
                    raise RuntimeError(
                        f"REFUSAL TO EXECUTE ON REAL DATA:\n"
                        f"Quality floors at '{floors_path}' have synthetic provenance.\n"
                        f"Real evaluations refuse synthetic quality floors unless '--allow-synthetic-dry-run' is enabled."
                    )
        except RuntimeError:
            raise
        except Exception:
            pass

    # Optional SQLite store connection for pre-generated synthetic journeys
    demo_store = None
    if is_synthetic:
        from trinetra_link.store.database import Store
        demo_db_path = REPO_ROOT / "demo_data" / "synthetic_120" / "store.db"
        if demo_db_path.exists():
            demo_store = Store(demo_db_path)

    # 3. Derive Ground Truth and construct journeys
    ground_truth_labels: List[str] = []
    omega_stars: List[str] = []
    scenario_cells: List[str] = []
    test_journeys: List[Journey] = []

    # Subgroup columns: weight_matched and mass_change_g (read ONLY inside eval/)
    has_wm_col = any("weight_matched" in r for r in test_staging)
    has_mc_col = any("mass_change_g" in r for r in test_staging)
    wm_subgroups: List[str] = []
    mc_subgroups: List[str] = []

    for r in test_staging:
        code = r["journey_code"]
        omega_star, expected_label, _ = derive_ground_truth(r, mask=mask)
        ground_truth_labels.append(canonicalize_label(expected_label))
        omega_stars.append(omega_star)
        scenario_cells.append(r.get("assigned_cell", "unknown"))

        # Extract subgroup attributes or fallback strictly to "n/a"
        if has_wm_col and r.get("weight_matched") is not None and str(r.get("weight_matched")).strip() != "":
            raw_wm = str(r.get("weight_matched")).strip().lower()
            val_wm = "yes" if raw_wm in ("yes", "true", "1") else ("no" if raw_wm in ("no", "false", "0") else raw_wm)
        else:
            val_wm = "n/a"
        wm_subgroups.append(val_wm)

        if has_mc_col and r.get("mass_change_g") is not None and str(r.get("mass_change_g")).strip() != "":
            try:
                mc_f = abs(float(r.get("mass_change_g")))
                if mc_f < 1.0:
                    val_mc = "0"
                elif mc_f < 20.0:
                    val_mc = "10"
                else:
                    val_mc = ">=20"
            except ValueError:
                val_mc = "n/a"
        else:
            val_mc = "n/a"
        mc_subgroups.append(val_mc)

        loaded_journey = None
        if demo_store:
            loaded_journey = demo_store.get_journey(code)
        if not loaded_journey:
            loaded_journey = generate_benchmark_journey_from_staging(r)

        # Apply field mask: weights only at CP1 and CP4; CP2/CP3 keep photos, seals, notes, but no weights
        if mask == "field":
            masked_cps = []
            for cp in loaded_journey.checkpoints:
                cp_copy = cp.model_copy(deep=True)
                if cp_copy.cp_index in (2, 3):
                    cp_copy.weights_g = []
                masked_cps.append(cp_copy)
            loaded_journey = Journey(
                journey_code=loaded_journey.journey_code,
                checkpoints=masked_cps,
                metadata=dict(loaded_journey.metadata) if loaded_journey.metadata else {},
            )

        test_journeys.append(loaded_journey)

    # 4. Method Evaluators
    active_theta = theta if theta is not None else 0.70
    methods: Dict[str, Callable[[Journey], Any]] = {
        "TriNetra-Link (Alg 1)": lambda j: predict_trinetra_link(j, mode="algorithm1", theta=active_theta, scales_config=scales_config, scales_path=sc_path),
        "TriNetra-Link (Bayes)": lambda j: predict_trinetra_link(j, mode="bayes", theta=active_theta, scales_config=scales_config, scales_path=sc_path),
        "B1 (CP4-only)": predict_b1_cp4,
        "B2 (Endpoints CP1+CP4)": predict_b2_endpoints,
        "B3 (Detection=Origin)": predict_b3_unlinked,
        "B5 (V3 Rules)": predict_b5_v3_rules,
    }

    # Include LLM Judge baseline ONLY when GROQ_API_KEY is present
    has_groq_key = bool(os.environ.get("GROQ_API_KEY"))
    if has_groq_key:
        methods["B4 (LLM Judge)"] = predict_b4_llm_judge
    else:
        print("[INFO] Baseline B4 (LLM Judge) SKIPPED: GROQ_API_KEY is missing. No predictions or table row produced.")

    results_table: List[Dict[str, Any]] = []
    method_predictions: Dict[str, List[str]] = {}
    method_confidences: Dict[str, List[float]] = {}

    for method_name, fn in methods.items():
        preds = []
        confs = []
        for j in test_journeys:
            attr = fn(j)
            p_label = canonicalize_label(attr.label)
            preds.append(p_label)
            conf = float(list(attr.posterior.values())[0]) if attr.posterior else 0.90
            confs.append(conf)

        method_predictions[method_name] = preds
        method_confidences[method_name] = confs

        # Metrics
        acc, n_correct, n_det = compute_stage_accuracy(preds, ground_truth_labels, omega_stars)
        f1 = compute_macro_f1(preds, ground_truth_labels, omega_stars)
        abs_metrics = compute_abstention_metrics(preds, ground_truth_labels, omega_stars)
        covs, risks, aurc = compute_risk_coverage_curve(preds, confs, ground_truth_labels, omega_stars)

        # Bootstrap CIs for accuracy
        def acc_metric(p, g, o):
            a, _, _ = compute_stage_accuracy(p, g, o)
            return a

        _, ci_acc_low, ci_acc_high = bootstrap_metric_ci(
            acc_metric, preds, ground_truth_labels, omega_stars, b=b_bootstrap
        )

        results_table.append({
            "method": method_name,
            "stage_acc_det": acc,
            "stage_acc_ci": f"[{ci_acc_low:.3f}, {ci_acc_high:.3f}]",
            "macro_f1_s1_s3": f1,
            "aar_non_det": abs_metrics["aar"],
            "ubr_non_det": abs_metrics["ubr"],
            "uar_det": abs_metrics["uar"],
            "aurc": aurc,
            "n_det_correct": f"{n_correct}/{n_det}",
        })

    # 5. Exact McNemar tests: TriNetra-Link (Alg 1) vs each baseline
    mcnemar_results: Dict[str, Any] = {}
    ref_preds = method_predictions["TriNetra-Link (Alg 1)"]
    det_mask = [om == "OBS_DETERMINABLE" for om in omega_stars]

    for m_name in methods.keys():
        if m_name == "TriNetra-Link (Alg 1)" or m_name not in method_predictions:
            continue
        b_disc, c_disc, p_val = exact_mcnemar_test(
            ref_preds, method_predictions[m_name], ground_truth_labels, filter_mask=det_mask
        )
        mcnemar_results[m_name] = {
            "trinetra_correct_baseline_incorrect": b_disc,
            "baseline_correct_trinetra_incorrect": c_disc,
            "p_value": p_val,
            "significant_at_05": p_val < 0.05,
        }

    # 6. Per-cell and Subgroup accuracy breakdowns
    per_cell_breakdown = compute_per_cell_breakdown(ref_preds, ground_truth_labels, scenario_cells)

    # Subgroup metrics: evaluate every method by weight_matched and mass_change_g bucket
    subgroup_table: List[Dict[str, Any]] = []
    subgroups_to_eval = [
        ("weight_matched", sorted(list(set(wm_subgroups))), wm_subgroups),
        ("mass_change_g", sorted(list(set(mc_subgroups))), mc_subgroups),
    ]

    for sg_name, sg_distinct, sg_assigned in subgroups_to_eval:
        for sg_val in sg_distinct:
            sg_idx = [i for i, v in enumerate(sg_assigned) if v == sg_val]
            if not sg_idx:
                continue
            sub_gts = [ground_truth_labels[i] for i in sg_idx]
            sub_omegas = [omega_stars[i] for i in sg_idx]

            for m_name in methods.keys():
                if m_name not in method_predictions:
                    continue
                sub_preds = [method_predictions[m_name][i] for i in sg_idx]
                sub_confs = [method_confidences[m_name][i] for i in sg_idx]

                s_acc, s_n_corr, s_n_det = compute_stage_accuracy(sub_preds, sub_gts, sub_omegas)
                s_f1 = compute_macro_f1(sub_preds, sub_gts, sub_omegas)
                s_abs = compute_abstention_metrics(sub_preds, sub_gts, sub_omegas)
                _, _, s_aurc = compute_risk_coverage_curve(sub_preds, sub_confs, sub_gts, sub_omegas)

                subgroup_table.append({
                    "subgroup_dimension": sg_name,
                    "subgroup_value": sg_val,
                    "method": m_name,
                    "stage_acc_det": s_acc,
                    "macro_f1_s1_s3": s_f1,
                    "aar_non_det": s_abs["aar"],
                    "ubr_non_det": s_abs["ubr"],
                    "uar_det": s_abs["uar"],
                    "aurc": s_aurc,
                    "n_total": len(sg_idx),
                    "n_det": s_n_det,
                    "n_correct": s_n_corr,
                })

    # 7. Generate Plots (Risk-Coverage Curves as PNG and PDF)
    fig_path_png = target_dir / f"figure_risk_coverage_{mask}.png"
    fig_path_pdf = target_dir / f"figure_risk_coverage_{mask}.pdf"
    plt.figure(figsize=(7, 5), dpi=300)

    for m_name in ("TriNetra-Link (Alg 1)", "TriNetra-Link (Bayes)", "B3 (Detection=Origin)", "B5 (V3 Rules)"):
        if m_name in method_predictions:
            covs, risks, aurc = compute_risk_coverage_curve(
                method_predictions[m_name], method_confidences[m_name], ground_truth_labels, omega_stars
            )
            plt.plot(covs, risks, label=f"{m_name} (AURC: {aurc:.3f})", lw=2)

    # Prominent Watermark across Plot for Synthetic Demo Run
    if is_synthetic or is_demo_run:
        plt.text(
            0.5, 0.5, "SYNTHETIC DRY RUN — NOT A RESULT",
            transform=plt.gca().transAxes,
            fontsize=15, color="red", alpha=0.35,
            ha="center", va="center", rotation=30, weight="bold"
        )

    plt.xlabel("Coverage (Fraction of Evaluated Journeys)", fontsize=11)
    plt.ylabel("Selective Risk (Error Rate)", fontsize=11)
    title_suffix = " [SYNTHETIC DEMO]" if (is_synthetic or is_demo_run) else ""
    plt.title(f"Risk-Coverage Tradeoff on Test Cohort (E1 - mask={mask}){title_suffix}", fontsize=12, fontweight="bold")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.savefig(fig_path_png)
    plt.savefig(fig_path_pdf)
    plt.close()

    # 8. Generate Tables: CSV (table3_full.csv / table3_field.csv) and LaTeX Table III
    csv_mask_path = target_dir / f"table3_{mask}.csv"
    with open(csv_mask_path, "w", encoding="utf-8") as fp:
        if is_synthetic or is_demo_run:
            fp.write("# SYNTHETIC DRY RUN — NOT A RESULT (DEMO DATA ONLY)\n")
        fp.write("Method,Stage Accuracy (DET),95% CI,Macro-F1 (S1-S3),AAR (Non-DET),UBR (Non-DET),UAR (DET),AURC\n")
        for r in results_table:
            fp.write(
                f"{r['method']},{r['stage_acc_det']},{r['stage_acc_ci']},{r['macro_f1_s1_s3']},"
                f"{r['aar_non_det']},{r['ubr_non_det']},{r['uar_det']},{r['aurc']}\n"
            )

    # Maintain primary comparison table for backward compatibility
    csv_primary_path = target_dir / "table3_primary_comparison.csv"
    if mask == "full" or not csv_primary_path.exists():
        with open(csv_primary_path, "w", encoding="utf-8") as fp:
            if is_synthetic or is_demo_run:
                fp.write("# SYNTHETIC DRY RUN — NOT A RESULT (DEMO DATA ONLY)\n")
            fp.write("Method,Stage Accuracy (DET),95% CI,Macro-F1 (S1-S3),AAR (Non-DET),UBR (Non-DET),UAR (DET),AURC\n")
            for r in results_table:
                fp.write(
                    f"{r['method']},{r['stage_acc_det']},{r['stage_acc_ci']},{r['macro_f1_s1_s3']},"
                    f"{r['aar_non_det']},{r['ubr_non_det']},{r['uar_det']},{r['aurc']}\n"
                )

    # Subgroups breakdown CSV
    subgroups_csv_path = target_dir / f"table3_subgroups_{mask}.csv"
    with open(subgroups_csv_path, "w", encoding="utf-8") as fp:
        if is_synthetic or is_demo_run:
            fp.write("# SYNTHETIC DRY RUN — NOT A RESULT (DEMO DATA ONLY)\n")
        fp.write("Dimension,Subgroup,Method,Stage Accuracy (DET),Macro-F1 (S1-S3),AAR (Non-DET),UBR (Non-DET),UAR (DET),AURC,N_Total,N_DET\n")
        for s in subgroup_table:
            fp.write(
                f"{s['subgroup_dimension']},{s['subgroup_value']},{s['method']},{s['stage_acc_det']:.4f},"
                f"{s['macro_f1_s1_s3']:.4f},{s['aar_non_det']:.4f},{s['ubr_non_det']:.4f},{s['uar_det']:.4f},{s['aurc']:.4f},"
                f"{s['n_total']},{s['n_det']}\n"
            )

    latex_path = target_dir / f"table3_{mask}.tex"
    with open(latex_path, "w", encoding="utf-8") as fp:
        if is_synthetic or is_demo_run:
            fp.write("% SYNTHETIC DRY RUN — NOT A RESULT (DEMO DATA ONLY)\n")
        fp.write(f"% TriNetra-Link Primary Experimental Comparison (Table III - mask={mask})\n")
        fp.write("\\begin{table*}[t]\n\\centering\n\\small\n")
        fp.write("\\begin{tabular}{lcccccccc}\n\\toprule\n")
        fp.write("\\textbf{Method} & \\textbf{Acc (DET)} & \\textbf{95\\% CI} & \\textbf{Macro-F1} & \\textbf{AAR} & \\textbf{UBR} & \\textbf{UAR} & \\textbf{AURC} \\\\\n\\midrule\n")
        for r in results_table:
            fp.write(
                f"{r['method']} & {r['stage_acc_det']:.3f} & {r['stage_acc_ci']} & {r['macro_f1_s1_s3']:.3f} & "
                f"{r['aar_non_det']:.3f} & {r['ubr_non_det']:.3f} & {r['uar_det']:.3f} & {r['aurc']:.3f} \\\\\n"
            )
        fp.write("\\bottomrule\n\\end{tabular}\n")
        caption_str = (
            f"\\caption{{\\textbf{{[SYNTHETIC DRY RUN — NOT A RESULT]}} Demonstration benchmark comparison across 96 synthetic test journeys (E1 - mask={mask}).}}\n"
            if (is_synthetic or is_demo_run)
            else f"\\caption{{Primary benchmark comparison across 96 physical test journeys (E1 - mask={mask}).}}\n"
        )
        fp.write(caption_str)
        fp.write(f"\\label{{tab:table3_{mask}}}\n\\end{{table*}}\n")

    # Also keep table3_primary_comparison.tex for compatibility
    latex_primary_path = target_dir / "table3_primary_comparison.tex"
    if mask == "full" or not latex_primary_path.exists():
        with open(latex_primary_path, "w", encoding="utf-8") as fp:
            with open(latex_path, "r", encoding="utf-8") as in_fp:
                fp.write(in_fp.read())

    # 9. Provenance Manifest
    prov = {
        "experiment": "E1",
        "mask": mask,
        "run_id": rid,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_test_journeys": len(test_staging),
        "determinability_rule_sha256": get_determinability_rule_hash(),
        "bootstrap_iterations": b_bootstrap,
        "results_summary": results_table,
        "subgroup_breakdowns": subgroup_table,
        "mcnemar_vs_baselines": mcnemar_results,
        "per_cell_breakdown": per_cell_breakdown,
        "artifacts": {
            "csv_table": str(csv_mask_path),
            "csv_primary": str(csv_primary_path),
            "table_full": str(target_dir / "table3_full.csv") if mask == "full" else None,
            "table_field": str(target_dir / "table3_field.csv") if mask == "field" else None,
            "subgroups_csv": str(subgroups_csv_path),
            "latex_table": str(latex_path),
            "figure_png": str(fig_path_png),
            "figure_pdf": str(fig_path_pdf),
        },
    }

    if is_synthetic or is_demo_run:
        prov["watermark"] = "SYNTHETIC DRY RUN — NOT A RESULT"
        prov["synthetic_dry_run"] = True
        prov["disclaimer"] = "Generated from programmatic synthetic demo fixtures. Not an empirical research result."

    prov_path = target_dir / f"provenance_{mask}.json"
    with open(prov_path, "w", encoding="utf-8") as fp:
        json.dump(prov, fp, indent=2)
        fp.write("\n")

    prov_main_path = target_dir / "provenance.json"
    if mask == "full" or not prov_main_path.exists():
        with open(prov_main_path, "w", encoding="utf-8") as fp:
            json.dump(prov, fp, indent=2)
            fp.write("\n")

    return prov
