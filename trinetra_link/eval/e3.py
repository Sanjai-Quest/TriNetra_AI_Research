from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — no Tk/display needed
import matplotlib.pyplot as plt
import numpy as np

from trinetra_link.config import DERIVED_DATA_DIR, REPO_ROOT, RESULTS_DIR
from trinetra_link.eval.e1 import generate_benchmark_journey_from_staging
from trinetra_link.eval.metrics import (
    compute_abstention_metrics,
    compute_macro_f1,
    compute_risk_coverage_curve,
    compute_stage_accuracy,
)
from trinetra_link.eval.pipeline import canonicalize_label, predict_trinetra_link
from trinetra_link.schema.models import Journey
from trinetra_link.staging.determinability import derive_ground_truth, get_determinability_rule_hash
from trinetra_link.staging.log import load_staging_log


def evaluate_e3(
    split_manifest_path: Optional[Path | str] = None,
    staging_log_path: Optional[Path | str] = None,
    scales_path: Optional[Path | str] = None,
    output_dir: Optional[Path | str] = None,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute Experiment E3: Architectural Ablation Analysis.
    Evaluates components on the 96 test captures:
      - Full Pipeline (Algorithm 1)
      - Full Pipeline (Bayesian Posterior)
      - Ablation 1: No Quality Gate (all q_k = 1.0)
      - Ablation 2: No Visual Reconciler
      - Ablation 3: Fixed 2.0g Weight Threshold (uncalibrated)
    """
    rid = run_id or f"e3_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    target_dir = Path(output_dir) if output_dir else RESULTS_DIR / rid
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load split manifest
    s_path = Path(split_manifest_path) if split_manifest_path else DERIVED_DATA_DIR / "split_manifest.json"
    if not s_path.exists():
        raise FileNotFoundError(f"Split manifest not found at {s_path}")

    with open(s_path, "r", encoding="utf-8") as f:
        split_data = json.load(f)

    test_codes = set(split_data.get("test_journey_codes", []))

    # 2. Load staging log
    staging_rows = load_staging_log(staging_log_path)
    if not staging_rows:
        assign_csv = REPO_ROOT / "data" / "restricted" / "staging_assignment_120.csv"
        if assign_csv.exists():
            import csv
            with open(assign_csv, "r", encoding="utf-8") as fp:
                staging_rows = list(csv.DictReader(fp))
                for r in staging_rows:
                    r["manipulation_interval"] = r.get("target_interval", "none")

    test_staging = [r for r in staging_rows if r["journey_code"] in test_codes]
    test_journeys = [generate_benchmark_journey_from_staging(r) for r in test_staging]

    # Load scales config
    scales_config = None
    sc_path = Path(scales_path) if scales_path else DERIVED_DATA_DIR / "scales.json"
    if sc_path.exists():
        try:
            with open(sc_path, "r", encoding="utf-8") as fp:
                scales_config = json.load(fp)
        except Exception:
            pass

    # Derive Ground Truth
    ground_truths = []
    omega_stars = []
    for r in test_staging:
        omega_star, exp_label, _ = derive_ground_truth(r)
        ground_truths.append(canonicalize_label(exp_label))
        omega_stars.append(omega_star)

    # Ablation configurations
    ablation_configs: Dict[str, Callable[[Journey], Any]] = {
        "TriNetra-Link (Full - Alg 1)": lambda j: predict_trinetra_link(j, mode="algorithm1", scales_config=scales_config),
        "TriNetra-Link (Full - Bayes)": lambda j: predict_trinetra_link(j, mode="bayes", scales_config=scales_config),
        "Ablation: No Quality Gate (q=1)": lambda j: predict_trinetra_link(j, mode="algorithm1", disable_quality_gate=True),
        "Ablation: No Visual Reconciler": lambda j: predict_trinetra_link(j, mode="algorithm1", disable_visual=True),
        "Ablation: Fixed 2g Weight Thresh": lambda j: predict_trinetra_link(j, mode="algorithm1", fixed_weight_threshold=2.0),
    }

    results_table: List[Dict[str, Any]] = []

    for name, fn in ablation_configs.items():
        preds = []
        confs = []
        for j in test_journeys:
            attr = fn(j)
            p_label = canonicalize_label(attr.label)
            preds.append(p_label)
            conf = float(list(attr.posterior.values())[0]) if attr.posterior else 0.90
            confs.append(conf)

        acc, n_corr, n_det = compute_stage_accuracy(preds, ground_truths, omega_stars)
        f1 = compute_macro_f1(preds, ground_truths, omega_stars)
        abs_m = compute_abstention_metrics(preds, ground_truths, omega_stars)
        _, _, aurc = compute_risk_coverage_curve(preds, confs, ground_truths, omega_stars)

        results_table.append({
            "model_variant": name,
            "stage_acc_det": acc,
            "macro_f1": f1,
            "aar_non_det": abs_m["aar"],
            "ubr_non_det": abs_m["ubr"],
            "uar_det": abs_m["uar"],
            "aurc": aurc,
            "n_det_correct": f"{n_corr}/{n_det}",
        })

    # Save CSV and LaTeX Tables
    csv_path = target_dir / "table_e3_ablations.csv"
    with open(csv_path, "w", encoding="utf-8") as fp:
        fp.write("Model Variant,Stage Acc (DET),Macro-F1 (S1-S3),AAR (Non-DET),UBR (Non-DET),UAR (DET),AURC\n")
        for r in results_table:
            fp.write(f"{r['model_variant']},{r['stage_acc_det']},{r['macro_f1']},{r['aar_non_det']},{r['ubr_non_det']},{r['uar_det']},{r['aurc']}\n")

    latex_path = target_dir / "table_e3_ablations.tex"
    with open(latex_path, "w", encoding="utf-8") as fp:
        fp.write("% TriNetra-Link Architectural Ablations (E3)\n\\begin{table}[t]\n\\centering\n\\small\n")
        fp.write("\\begin{tabular}{lccccc}\n\\toprule\n\\textbf{Variant} & \\textbf{Acc (DET)} & \\textbf{Macro-F1} & \\textbf{AAR} & \\textbf{UBR} & \\textbf{AURC} \\\\\n\\midrule\n")
        for r in results_table:
            fp.write(f"{r['model_variant']} & {r['stage_acc_det']:.3f} & {r['macro_f1']:.3f} & {r['aar_non_det']:.3f} & {r['ubr_non_det']:.3f} & {r['aurc']:.3f} \\\\\n")
        fp.write("\\bottomrule\n\\end{tabular}\n\\caption{Architectural ablation study on 96 test journeys (E3).}\n\\end{table}\n")

    # Plot Ablations Bar Chart
    fig_png = target_dir / "figure_ablations.png"
    fig_pdf = target_dir / "figure_ablations.pdf"

    variants = [r["model_variant"].replace("Ablation: ", "") for r in results_table]
    accs = [r["stage_acc_det"] for r in results_table]
    aars = [r["aar_non_det"] for r in results_table]

    x = np.arange(len(variants))
    width = 0.35

    plt.figure(figsize=(9, 4.8), dpi=300)
    plt.bar(x - width / 2, accs, width, label="Stage Accuracy (DET)", color="#2ca02c")
    plt.bar(x + width / 2, aars, width, label="Appropriate Abstention Rate (AAR)", color="#ff7f0e")
    plt.xticks(x, variants, rotation=15, ha="right", fontsize=9)
    plt.ylabel("Score", fontsize=11)
    plt.title("Component Ablations Comparison (E3)", fontsize=12, fontweight="bold")
    plt.ylim(0.0, 1.1)
    plt.legend(loc="lower right")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(fig_png)
    plt.savefig(fig_pdf)
    plt.close()

    manifest = {
        "experiment": "E3",
        "run_id": rid,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_test_journeys": len(test_journeys),
        "results": results_table,
        "artifacts": {
            "csv_table": str(csv_path),
            "latex_table": str(latex_path),
            "figure_png": str(fig_png),
            "figure_pdf": str(fig_pdf),
        },
    }

    with open(target_dir / "provenance.json", "w", encoding="utf-8") as fp:
        json.dump(manifest, fp, indent=2)

    return manifest
