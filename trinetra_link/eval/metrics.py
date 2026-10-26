from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy import stats
from sklearn.metrics import confusion_matrix, f1_score


def compute_stage_accuracy(
    predictions: List[str],
    ground_truths: List[str],
    omega_stars: List[str],
) -> Tuple[float, int, int]:
    """
    Compute stage accuracy strictly on determinable journeys (Omega* = OBS_DETERMINABLE).
    Returns: (accuracy, correct_count, total_det_count)
    """
    correct = 0
    total = 0
    for pred, gt, omega in zip(predictions, ground_truths, omega_stars):
        if omega == "OBS_DETERMINABLE":
            total += 1
            if pred == gt:
                correct += 1

    acc = (correct / total) if total > 0 else 0.0
    return round(acc, 4), correct, total


def compute_macro_f1(
    predictions: List[str],
    ground_truths: List[str],
    omega_stars: List[str],
    target_stages: Optional[List[str]] = None,
) -> float:
    """
    Compute Macro-F1 across stages S1, S2, S3 for determinable journeys.
    """
    stages = target_stages or ["ATTR_STAGE(1)", "ATTR_STAGE(2)", "ATTR_STAGE(3)"]
    y_true: List[str] = []
    y_pred: List[str] = []

    for pred, gt, omega in zip(predictions, ground_truths, omega_stars):
        if omega == "OBS_DETERMINABLE" and gt in stages:
            y_true.append(gt)
            y_pred.append(pred)

    if not y_true:
        return 0.0

    score = float(f1_score(y_true, y_pred, labels=stages, average="macro", zero_division=0))
    return round(score, 4)


def compute_abstention_metrics(
    predictions: List[str],
    ground_truths: List[str],
    omega_stars: List[str],
) -> Dict[str, Any]:
    """
    Compute Appropriate Abstention Rate (AAR), Unwarranted Bounded-tamper Rate (UBR),
    and Unnecessary Abstention Rate (UAR).
      - AAR: fraction of non-determinable journeys correctly abstained
      - UBR: fraction of non-determinable journeys falsely attributed to a specific stage
      - UAR: fraction of determinable journeys where method unnecessarily abstains
    """
    abstain_labels = {"ATTR_ABSTAIN_DEGRADED", "ATTR_ABSTAIN_INDISTINGUISHABLE"}

    non_det_total = 0
    non_det_appropriate = 0
    non_det_unwarranted = 0

    det_total = 0
    det_unnecessary_abstain = 0

    for pred, gt, omega in zip(predictions, ground_truths, omega_stars):
        if omega in ("OBS_DEGRADED_INCOMPLETE", "OBS_INDISTINGUISHABLE"):
            non_det_total += 1
            if pred in abstain_labels:
                non_det_appropriate += 1
            elif pred.startswith("ATTR_STAGE("):
                non_det_unwarranted += 1
        elif omega == "OBS_DETERMINABLE":
            det_total += 1
            if pred in abstain_labels:
                det_unnecessary_abstain += 1

    aar = (non_det_appropriate / non_det_total) if non_det_total > 0 else 1.0
    ubr = (non_det_unwarranted / non_det_total) if non_det_total > 0 else 0.0
    uar = (det_unnecessary_abstain / det_total) if det_total > 0 else 0.0

    return {
        "aar": round(aar, 4),
        "ubr": round(ubr, 4),
        "uar": round(uar, 4),
        "non_det_total": non_det_total,
        "non_det_appropriate": non_det_appropriate,
        "non_det_unwarranted": non_det_unwarranted,
        "det_total": det_total,
        "det_unnecessary_abstain": det_unnecessary_abstain,
    }


def compute_risk_coverage_curve(
    predictions: List[str],
    confidences: List[float],
    ground_truths: List[str],
    omega_stars: List[str],
    n_points: int = 20,
) -> Tuple[List[float], List[float], float]:
    """
    Compute selective risk-coverage curve and Area Under Risk-Coverage curve (AURC).
    Sorts predictions by confidence, computes error rate (risk) as coverage increases.
    Returns: (coverages, risks, aurc)
    """
    det_items = [
        (c, p == gt)
        for c, p, gt, omega in zip(confidences, predictions, ground_truths, omega_stars)
        if omega == "OBS_DETERMINABLE"
    ]
    if not det_items:
        return [0.0, 1.0], [0.0, 0.0], 0.0

    # Sort descending by confidence
    det_items.sort(key=lambda x: x[0], reverse=True)
    n = len(det_items)

    coverages: List[float] = []
    risks: List[float] = []

    for k in range(1, n + 1):
        subset = det_items[:k]
        cov = k / n
        errors = sum(1 for _, correct in subset if not correct)
        risk = errors / k
        coverages.append(round(cov, 4))
        risks.append(round(risk, 4))

    # Compute trapezoidal AURC
    aurc = float(np.trapezoid(risks, coverages)) if hasattr(np, "trapezoid") else float(np.trapz(risks, coverages))
    return coverages, risks, round(aurc, 4)


def compute_per_cell_breakdown(
    predictions: List[str],
    ground_truths: List[str],
    scenario_cells: List[str],
) -> Dict[str, Dict[str, int]]:
    """
    Compute per-cell accuracy numerators and denominators across the 8 scenario cells.
    """
    breakdown: Dict[str, Dict[str, int]] = {}
    for pred, gt, cell in zip(predictions, ground_truths, scenario_cells):
        if cell not in breakdown:
            breakdown[cell] = {"correct": 0, "total": 0}
        breakdown[cell]["total"] += 1
        if pred == gt:
            breakdown[cell]["correct"] += 1

    return breakdown


def bootstrap_metric_ci(
    metric_fn: Any,
    predictions: List[str],
    ground_truths: List[str],
    auxiliary: List[Any],
    b: int = 2000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """
    Compute empirical journey-level bootstrap confidence interval (B=2000 iterations).
    Returns: (point_estimate, ci_lower, ci_upper)
    """
    n = len(predictions)
    if n == 0:
        return 0.0, 0.0, 0.0

    rng = np.random.default_rng(seed)
    point_est = float(metric_fn(predictions, ground_truths, auxiliary))

    bootstrap_estimates = []
    for _ in range(b):
        indices = rng.integers(0, n, size=n)
        b_pred = [predictions[i] for i in indices]
        b_gt = [ground_truths[i] for i in indices]
        b_aux = [auxiliary[i] for i in indices]
        val = metric_fn(b_pred, b_gt, b_aux)
        bootstrap_estimates.append(float(val))

    ci_lower = float(np.percentile(bootstrap_estimates, 100 * (alpha / 2)))
    ci_upper = float(np.percentile(bootstrap_estimates, 100 * (1 - alpha / 2)))

    return round(point_est, 4), round(ci_lower, 4), round(ci_upper, 4)


def exact_mcnemar_test(
    preds_a: List[str],
    preds_b: List[str],
    ground_truths: List[str],
    filter_mask: Optional[List[bool]] = None,
) -> Tuple[int, int, float]:
    """
    Exact two-sided McNemar paired comparison test.
      - b_discordant: Method A correct, Method B incorrect
      - c_discordant: Method B correct, Method A incorrect
    Returns: (b_discordant, c_discordant, p_value)
    """
    b_discordant = 0
    c_discordant = 0

    for idx, (p_a, p_b, gt) in enumerate(zip(preds_a, preds_b, ground_truths)):
        if filter_mask is not None and not filter_mask[idx]:
            continue
        corr_a = (p_a == gt)
        corr_b = (p_b == gt)

        if corr_a and not corr_b:
            b_discordant += 1
        elif corr_b and not corr_a:
            c_discordant += 1

    total_discordant = b_discordant + c_discordant
    if total_discordant == 0:
        p_val = 1.0
    else:
        # Exact two-sided binomial test under H0: p = 0.5
        p_val = float(stats.binomtest(b_discordant, total_discordant, p=0.5, alternative="two-sided").pvalue)

    return b_discordant, c_discordant, round(p_val, 5)
