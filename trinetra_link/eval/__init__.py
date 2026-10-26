"""
TriNetra-Link Evaluation & Experiment Suite (Phase D / Amendment v2.6).
"""
from trinetra_link.eval.e1 import evaluate_e1
from trinetra_link.eval.e2 import evaluate_e2
from trinetra_link.eval.e3 import evaluate_e3
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

__all__ = [
    "evaluate_e1",
    "evaluate_e2",
    "evaluate_e3",
    "compute_stage_accuracy",
    "compute_macro_f1",
    "compute_abstention_metrics",
    "compute_risk_coverage_curve",
    "compute_per_cell_breakdown",
    "bootstrap_metric_ci",
    "exact_mcnemar_test",
    "canonicalize_label",
    "predict_trinetra_link",
]
