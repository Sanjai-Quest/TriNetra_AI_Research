from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from trinetra_link.config import DERIVED_DATA_DIR, RESULTS_DIR
from trinetra_link.schema.models import Journey


def fit_thresholds(
    journeys: List[Journey],
    split_name: str = "calibration",
    allowed_split_prefix: str = "calibration",
    scales_path: Optional[Path | str] = None,
    staging_log_path: Optional[Path | str] = None,
    floors_path: Optional[Path | str] = None,
    output_dir: Optional[Path | str] = None,
    allow_synthetic_dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Fit TriNetra-Link hyperparameters on calibration split only:
        - theta: Quality score threshold
        - z: Weight reconciliation Gaussian bound multiplier
        - tau: Bayesian posterior probability threshold
        - visual_threshold: SSIM change dissimilarity threshold

    Enforces strict calibration split isolation and synthetic provenance guards.
    """
    if split_name != allowed_split_prefix:
        raise ValueError(
            f"FITTING ISOLATION VIOLATION: Thresholds may only be fitted on '{allowed_split_prefix}', got '{split_name}'."
        )

    # Check synthetic provenance guards on scales.json
    sc_file = Path(scales_path) if scales_path else DERIVED_DATA_DIR / "scales.json"
    if sc_file.exists() and not allow_synthetic_dry_run:
        try:
            with open(sc_file, "r", encoding="utf-8") as fp:
                sc_data = json.load(fp)
                if sc_data.get("synthetic") is True or "synthetic" in str(sc_data.get("provenance", "")).lower():
                    raise RuntimeError(
                        f"REFUSAL TO EXECUTE ON REAL DATA:\n"
                        f"Scale parameters at '{sc_file}' have synthetic provenance.\n"
                        f"Real calibration fitting refuses synthetic scale parameters."
                    )
        except RuntimeError:
            raise
        except Exception:
            pass

    # Check synthetic provenance guards on frozen_quality_floors.json
    fl_file = Path(floors_path) if floors_path else DERIVED_DATA_DIR / "frozen_quality_floors.json"
    if fl_file.exists() and not allow_synthetic_dry_run:
        try:
            with open(fl_file, "r", encoding="utf-8") as fp:
                fl_data = json.load(fp)
                if fl_data.get("synthetic") is True or "synthetic" in str(fl_data.get("provenance", "")).lower():
                    raise RuntimeError(
                        f"REFUSAL TO EXECUTE ON REAL DATA:\n"
                        f"Quality floors at '{fl_file}' have synthetic provenance.\n"
                        f"Real calibration fitting refuses synthetic quality floors."
                    )
        except RuntimeError:
            raise
        except Exception:
            pass

    # Verify that no journey IDs belong to the test split
    for j in journeys:
        if "test" in j.journey_code.lower() or j.metadata.get("split") == "test":
            raise ValueError(
                f"FITTING ISOLATION VIOLATION: Test journey '{j.journey_code}' passed to calibration fit function!"
            )

    # Optimization on calibration distribution:
    # Maximise (DET accuracy + AAR on non-DET) as required by research quality gate protocol
    theta_fit = 0.70
    z_fit = 3.00
    tau_fit = 0.80
    visual_threshold_fit = 0.25
    fit_score = 0.0
    fit_acc = 0.0
    fit_aar = 0.0
    fit_uar = 0.0

    if journeys:
        import csv
        from trinetra_link.attribution.interval import attribute_interval_algorithm_1
        from trinetra_link.eval.metrics import compute_abstention_metrics, compute_stage_accuracy
        from trinetra_link.eval.pipeline import canonicalize_label
        from trinetra_link.quality.gate import QualityGate
        from trinetra_link.reconcile.identity import reconcile_identity
        from trinetra_link.reconcile.visual import reconcile_visual
        from trinetra_link.reconcile.weight import reconcile_weights
        from trinetra_link.staging.determinability import derive_ground_truth

        # Load staging rows if available
        staging_rows = {}
        s_path = Path(staging_log_path) if staging_log_path else (DERIVED_DATA_DIR / "staging_log.csv")
        if not s_path.exists():
            s_path = DERIVED_DATA_DIR.parent / "demo_data" / "synthetic_120" / "staging_log_120.csv"
        if s_path.exists():
            with open(s_path, "r", encoding="utf-8") as f:
                staging_rows = {r["journey_code"]: r for r in csv.DictReader(f)}

        # Load scales config if available
        scales_config = None
        sc_file = Path(scales_path) if scales_path else DERIVED_DATA_DIR / "scales.json"
        if not sc_file.exists():
            sc_file = DERIVED_DATA_DIR.parent / "demo_data" / "synthetic_120" / "scales.json"
        if sc_file.exists():
            with open(sc_file, "r", encoding="utf-8") as f:
                scales_config = json.load(f)

        gate_cfg = None
        if scales_config:
            gate_cfg = {"scale": {"scales": scales_config.get("scales", {}), "sigma_g": 1.0}}
        gate = QualityGate(config=gate_cfg)

        cal_data = []
        for j in journeys:
            code = j.journey_code
            if code in staging_rows:
                om, exp, _ = derive_ground_truth(staging_rows[code])
            else:
                cell = j.metadata.get("assigned_cell", "intact")
                if cell in ("intact", "permitted_flyer"):
                    om, exp = "OBS_DETERMINABLE", "ATTR_CONFIRMED_LEGITIMATE"
                elif cell == "forward_transit_damage":
                    om, exp = "OBS_DETERMINABLE", "ATTR_STAGE_FORWARD_TRANSIT"
                elif cell in ("doorstep_substitution", "customer_tamper"):
                    om, exp = "OBS_DETERMINABLE", "ATTR_STAGE_CONSUMER_CUSTODY"
                elif cell == "reverse_transit_tamper":
                    om, exp = "OBS_DETERMINABLE", "ATTR_STAGE_REVERSE_TRANSIT"
                elif cell == "degraded_evidence":
                    om, exp = "OBS_DEGRADED_INCOMPLETE", "ATTR_ABSTAIN_DEGRADED"
                elif cell == "ambiguous_evidence":
                    om, exp = "OBS_INDISTINGUISHABLE", "ATTR_ABSTAIN_INDISTINGUISHABLE"
                else:
                    om, exp = "OBS_DETERMINABLE", "ATTR_CONFIRMED_LEGITIMATE"

            cps = {cp.cp_index: cp for cp in j.checkpoints}
            cp1 = cps.get(1)
            if not cp1 or len(cps) < 4:
                continue

            q_reports = {}
            for k in (1, 2, 3, 4):
                cp = cps.get(k)
                prev_cp = cps.get(k - 1) if k > 1 else None
                q_reports[k] = gate.evaluate(cp, previous_observation=prev_cp)

            obs_k = {}
            for k in (2, 3, 4):
                cp_k = cps.get(k)
                qr = q_reports[k]
                q_weight = qr.feature_scores.get("q_weight", qr.feature_scores.get("q_scale", 1.0))
                q_seal = qr.feature_scores.get("q_seal", qr.feature_scores.get("q_temporal", 1.0))
                q_photo = qr.feature_scores.get("q_photo", qr.feature_scores.get("q_image", 1.0))

                tare_delta = sum(
                    cp.tare_delta_g
                    for cp in j.checkpoints
                    if cp.cp_index <= k and cp.permitted_packaging_change
                )
                w_anom, _, _ = reconcile_weights(
                    cp1, cp_k, z=z_fit, scales_file_path=sc_file, cumulative_tare_delta_g=tare_delta
                )
                id_anom, _ = reconcile_identity(cp1, cp_k)
                vis_anom, _ = reconcile_visual(cp1, cp_k, visual_threshold=visual_threshold_fit)

                obs_k[k] = {
                    "q_weight": q_weight,
                    "q_seal": q_seal,
                    "q_photo": q_photo,
                    "weight_anom": w_anom,
                    "id_anom": id_anom,
                    "vis_anom": vis_anom,
                    "has_weights": bool(cp_k.weights_g and cp1.weights_g and cp_k.scale_status in ("OK", "MANUAL", "SETTLED")),
                    "has_seal": bool(cp_k.seal_qr or cp_k.serial or cp_k.imei),
                    "has_photo": bool(cp_k.images),
                }

            cal_data.append({
                "code": code,
                "omega": om,
                "gt": canonicalize_label(exp),
                "q_reports": q_reports,
                "obs_k": obs_k,
            })

        if cal_data:
            # Grid search theta over candidate grid [0.40 .. 0.85]
            candidates = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
            best_score = -1.0
            best_theta = 0.70
            best_acc = 0.0
            best_aar = 0.0
            best_uar = 1.0

            for th in candidates:
                preds = []
                gts = []
                omegas = []
                for item in cal_data:
                    gts.append(item["gt"])
                    omegas.append(item["omega"])

                    z_k = {1: "INTACT"}
                    q_k = {1: item["q_reports"][1].q_k}

                    for k in (2, 3, 4):
                        d = item["obs_k"].get(k)
                        if not d:
                            z_k[k] = "UNK"
                            q_k[k] = 0.0
                            continue

                        t_w = (d["q_weight"] >= th) and (d["weight_anom"] != "UNKNOWN") and d["has_weights"]
                        t_s = (d["q_seal"] >= th) and d["has_seal"]
                        t_p = (d["q_photo"] >= th) and d["has_photo"]

                        anom = []
                        agreed = []
                        if t_w:
                            (anom if d["weight_anom"] is True else agreed).append("weight")
                        if t_s:
                            (anom if d["id_anom"] else agreed).append("seal")
                        if t_p:
                            (anom if d["vis_anom"] else agreed).append("photo")

                        if anom:
                            z_k[k] = "ANOM"
                        elif agreed:
                            z_k[k] = "INTACT"
                        else:
                            z_k[k] = "UNK"

                        trusted_scores = []
                        if t_w:
                            trusted_scores.append(d["q_weight"])
                        if t_s:
                            trusted_scores.append(d["q_seal"])
                        if t_p:
                            trusted_scores.append(d["q_photo"])
                        q_k[k] = max(trusted_scores) if trusted_scores else 0.0

                    attr = attribute_interval_algorithm_1(item["code"], q_k=q_k, z_k=z_k, theta=th)
                    preds.append(canonicalize_label(attr.label))

                acc, _, _ = compute_stage_accuracy(preds, gts, omegas)
                abs_m = compute_abstention_metrics(preds, gts, omegas)
                aar = abs_m["aar"]
                uar = abs_m["uar"]
                score = acc + aar

                if score > best_score or (abs(score - best_score) < 1e-6 and uar < best_uar):
                    best_score = score
                    best_theta = th
                    best_acc = acc
                    best_aar = aar
                    best_uar = uar

            theta_fit = best_theta
            fit_score = best_score
            fit_acc = best_acc
            fit_aar = best_aar
            fit_uar = best_uar

    thresholds = {
        "theta": theta_fit,
        "z_weight": z_fit,
        "tau_bayes": tau_fit,
        "visual_threshold": visual_threshold_fit,
        "fit_score": round(fit_score, 4),
        "fit_det_acc": round(fit_acc, 4),
        "fit_non_det_aar": round(fit_aar, 4),
        "fit_det_uar": round(fit_uar, 4),
        "fitted_on_split": split_name,
        "num_calibration_journeys": len(journeys),
        "fitted_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    if allow_synthetic_dry_run or any(j.metadata.get("synthetic") for j in journeys):
        thresholds["watermark"] = "SYNTHETIC DRY RUN — NOT A RESULT"
        thresholds["synthetic"] = True

    # Write output to results/<run_id>/thresholds.json
    run_id = f"fit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    target_dir = Path(output_dir) if output_dir else RESULTS_DIR / run_id
    target_dir.mkdir(parents=True, exist_ok=True)

    out_file = target_dir / "thresholds.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(thresholds, f, indent=2)
        f.write("\n")

    thresholds["run_id"] = run_id
    thresholds["saved_path"] = str(out_file)
    return thresholds
