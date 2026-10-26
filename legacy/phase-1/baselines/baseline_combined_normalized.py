"""
Baseline: Combined Normalized Rules Model (Strong Multi-Signal Baseline)
Remediation C-16 (Audit Finding F-05).

Provides a rigorous competitive baseline that:
1. Applies all three core detection checks (Identity, Weight Anomaly, Timeline Chronology).
2. Uses the exact same normalization rules and thresholds as the primary TriNetra ReconciliationEngine:
   - Identity: exact normalized SKU / variant comparison
   - Weight: relative drop > 15% or 3-sigma statistical outlier
   - Timeline: chronological ordering across canonical lifecycle stages
3. Operates on the exact same multi-source evidence payload.

Purpose:
Serves as an honest, fair baseline. If TriNetra achieves similar F1 to this baseline,
it proves performance is driven by combining signals rather than opaque architectural claims.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np


class BaselineCombinedNormalized:
    """Strong combined multi-signal baseline applying normalized identity, weight, and timeline checks."""

    EVENT_HIERARCHY = {
        "ORDER": 1,
        "SELLER": 2,
        "WAREHOUSE": 3,
        "CARRIER": 4,
        "DELIVERY": 5,
        "RETURN": 6
    }

    WEIGHT_DROP_THRESHOLD = 0.15  # 15% drop matches ReconciliationEngine

    def predict(self, evidence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates normalized evidence records across identity, weight, and timeline signals.
        Returns a structured prediction matching baseline format:
        {'baseline': 'COMBINED_NORMALIZED', 'prediction': 'CONFLICT' | 'CONSISTENT', 'conflict_type': ..., 'reasoning': ...}
        """
        if not evidence_list:
            return {
                "baseline": "COMBINED_NORMALIZED",
                "prediction": "CONSISTENT",
                "conflict_type": None,
                "reasoning": "No evidence provided."
            }

        # 1. Identity Consistency Check
        identity_result = self._check_identity(evidence_list)
        if identity_result["has_conflict"]:
            return {
                "baseline": "COMBINED_NORMALIZED",
                "prediction": "CONFLICT",
                "conflict_type": "IDENTITY_CONFLICT",
                "reasoning": identity_result["reasoning"]
            }

        # 2. Weight Anomaly Check
        weight_result = self._check_weight(evidence_list)
        if weight_result["has_conflict"]:
            return {
                "baseline": "COMBINED_NORMALIZED",
                "prediction": "CONFLICT",
                "conflict_type": "WEIGHT_ANOMALY",
                "reasoning": weight_result["reasoning"]
            }

        # 3. Timeline Ordering Check
        timeline_result = self._check_timeline(evidence_list)
        if timeline_result["has_conflict"]:
            return {
                "baseline": "COMBINED_NORMALIZED",
                "prediction": "CONFLICT",
                "conflict_type": "TEMPORAL_CONFLICT",
                "reasoning": timeline_result["reasoning"]
            }

        return {
            "baseline": "COMBINED_NORMALIZED",
            "prediction": "CONSISTENT",
            "conflict_type": None,
            "reasoning": "All signals (identity, weight, timeline) are consistent within normalized bounds."
        }

    def _check_identity(self, evidence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        skus = []
        for ev in evidence_list:
            sku = ev.get("sku")
            if sku:
                skus.append(str(sku).strip().upper())

        if len(skus) > 1:
            first_sku = skus[0]
            for s in skus[1:]:
                if s != first_sku:
                    return {
                        "has_conflict": True,
                        "reasoning": f"SKU mismatch detected: {first_sku} vs {s}"
                    }
        return {"has_conflict": False, "reasoning": ""}

    def _check_weight(self, evidence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        weights = []
        for ev in evidence_list:
            w = ev.get("weight")
            if w is not None:
                try:
                    weights.append(float(w))
                except (ValueError, TypeError):
                    continue

        if len(weights) >= 2:
            outbound_weight = weights[0]
            for w in weights[1:]:
                if outbound_weight > 0:
                    drop_pct = (outbound_weight - w) / outbound_weight
                    if drop_pct > self.WEIGHT_DROP_THRESHOLD:
                        return {
                            "has_conflict": True,
                            "reasoning": f"Weight drop of {drop_pct:.1%} exceeds threshold ({self.WEIGHT_DROP_THRESHOLD:.0%}): {outbound_weight}g -> {w}g"
                        }

        # 3-sigma statistical check
        if len(weights) >= 3:
            mean_w = np.mean(weights)
            std_w = np.std(weights)
            if std_w > 0:
                for w in weights:
                    if abs(w - mean_w) > 3 * std_w:
                        return {
                            "has_conflict": True,
                            "reasoning": f"Weight reading {w}g exceeds 3 standard deviations from mean {mean_w:.1f}g (std={std_w:.1f}g)"
                        }

        return {"has_conflict": False, "reasoning": ""}

    def _check_timeline(self, evidence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        parsed_events = []
        for ev in evidence_list:
            source = str(ev.get("source", "")).strip().upper()
            ts_str = ev.get("timestamp")
            if source in self.EVENT_HIERARCHY and ts_str:
                try:
                    dt = datetime.strptime(str(ts_str)[:19], "%Y-%m-%dT%H:%M:%S")
                    parsed_events.append((self.EVENT_HIERARCHY[source], source, dt))
                except Exception:
                    continue

        if len(parsed_events) >= 2:
            for i in range(len(parsed_events)):
                for j in range(i + 1, len(parsed_events)):
                    rank_i, source_i, dt_i = parsed_events[i]
                    rank_j, source_j, dt_j = parsed_events[j]
                    if rank_i < rank_j and dt_i > dt_j:
                        return {
                            "has_conflict": True,
                            "reasoning": f"Temporal inversion: {source_i} ({dt_i}) logged after subsequent checkpoint {source_j} ({dt_j})"
                        }
                    elif rank_i > rank_j and dt_i < dt_j:
                        return {
                            "has_conflict": True,
                            "reasoning": f"Temporal inversion: {source_i} ({dt_i}) logged before prior checkpoint {source_j} ({dt_j})"
                        }

        return {"has_conflict": False, "reasoning": ""}
