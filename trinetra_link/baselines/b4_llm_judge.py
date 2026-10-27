from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

import numpy as np

from trinetra_link.config import REPO_ROOT
from trinetra_link.schema.models import Attribution, CheckpointObservation, Journey

PROMPT_TEMPLATE_PATH = REPO_ROOT / "baselines" / "prompts" / "llm_judge_v1.txt"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


def format_journey_as_text(journey: Journey) -> str:
    """Format the 4 checkpoint observation records into structured text for LLM judge."""
    lines = [f"Journey Identifier: {journey.journey_code}"]
    for cp in sorted(journey.checkpoints, key=lambda x: x.cp_index):
        w_mean = float(np.mean(cp.weights_g)) if cp.weights_g else 0.0
        lines.append(f"\n--- Checkpoint {cp.cp_index} ---")
        lines.append(f"  Timestamp (UTC): {cp.ts_utc}")
        lines.append(f"  Device ID: {cp.device_id} | Operator ID: {cp.operator_id}")
        lines.append(f"  Scale ID: {cp.scale_id} | Status: {cp.scale_status}")
        lines.append(f"  Weight Readings (g): {cp.weights_g} (mean: {w_mean:.2f}g)")
        if cp.permitted_packaging_change:
            lines.append(f"  Permitted Packaging Change: YES (tare adjustment: {cp.tare_delta_g:+.2f}g)")
        if cp.seal_qr:
            lines.append(f"  Security Seal QR: {cp.seal_qr}")
        if cp.serial:
            lines.append(f"  Hardware Serial: {cp.serial}")
        if cp.imei:
            lines.append(f"  Hardware IMEI: {cp.imei}")
        if cp.images:
            lines.append(f"  Photographic Evidence: {len(cp.images)} photo(s) captured ({', '.join(p.side for p in cp.images)})")
        if cp.carrier_log:
            lines.append(f"  Carrier Notes: {cp.carrier_log}")

    return "\n".join(lines)


def build_judge_prompt(journey: Journey, template_path: Optional[Path | str] = None) -> str:
    """Load prompt template and interpolate journey structured text."""
    p_path = Path(template_path) if template_path else PROMPT_TEMPLATE_PATH
    if not p_path.exists():
        template_content = (
            "You are a forensic auditor. Analyze the journey observations:\n"
            "{{JOURNEY_OBSERVATIONS_TEXT}}\n"
            "Return JSON: {\"label\": \"<LABEL>\", \"confidence\": 0.9, \"rationale\": \"...\"}"
        )
    else:
        template_content = p_path.read_text(encoding="utf-8")

    obs_text = format_journey_as_text(journey)
    return template_content.replace("{{JOURNEY_OBSERVATIONS_TEXT}}", obs_text)


def query_groq_llm(
    prompt: str,
    api_key: str,
    model: str = DEFAULT_GROQ_MODEL,
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """Execute live Groq API call with llama-3.3-70b-versatile."""
    payload = {
        "model": model,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GROQ_API_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TriNetra-Link-Research/2.6.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        content = res_data["choices"][0]["message"]["content"]
        return json.loads(content)


def predict_b4_llm_judge(
    journey: Journey,
    groq_api_key: Optional[str] = None,
    runs: int = 3,
) -> Attribution:
    """
    Baseline B4: LLM Judge using Groq llama-3.3-70b-versatile (temp 0, 3 runs).
    Requires GROQ_API_KEY. If key is missing, raises RuntimeError.
    Offline deterministic judge fallback has been removed per research protocol audit.
    """
    api_key = groq_api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Baseline B4 (LLM Judge) cannot execute without a valid Groq API key."
        )

    prompt = build_judge_prompt(journey)
    responses: List[Dict[str, Any]] = []

    # Run repeated live inference queries as required by protocol
    for _ in range(max(1, runs)):
        res = query_groq_llm(prompt, api_key=api_key, model=DEFAULT_GROQ_MODEL, temperature=0.0)
        responses.append(res)

    # Majority voting over the runs
    labels = [r.get("label", "ATTR_ABSTAIN_DEGRADED") for r in responses]
    counter = Counter(labels)
    consensus_label = counter.most_common(1)[0][0]
    avg_conf = float(np.mean([r.get("confidence", 0.5) for r in responses if r.get("label") == consensus_label]))

    # Map consensus label to canonical protocol label strings
    if consensus_label in ("ATTR_STAGE_FORWARD_TRANSIT", "ATTR_STAGE(1)", "STAGE(1)"):
        consensus_label = "ATTR_STAGE_FORWARD_TRANSIT"
        interval = [1, 2]
    elif consensus_label in ("ATTR_STAGE_CONSUMER_CUSTODY", "ATTR_STAGE(2)", "STAGE(2)"):
        consensus_label = "ATTR_STAGE_CONSUMER_CUSTODY"
        interval = [2, 3]
    elif consensus_label in ("ATTR_STAGE_REVERSE_TRANSIT", "ATTR_STAGE(3)", "STAGE(3)"):
        consensus_label = "ATTR_STAGE_REVERSE_TRANSIT"
        interval = [3, 4]
    elif consensus_label in ("ATTR_CONFIRMED_LEGITIMATE", "LEGITIMATE"):
        consensus_label = "ATTR_CONFIRMED_LEGITIMATE"
        interval = [1, 4]
    elif consensus_label in ("ATTR_ABSTAIN_INDISTINGUISHABLE", "ABSTAIN_INDISTINGUISHABLE"):
        consensus_label = "ATTR_ABSTAIN_INDISTINGUISHABLE"
        interval = None
    else:
        consensus_label = "ATTR_ABSTAIN_DEGRADED"
        interval = None

    rationale = responses[0].get("rationale", f"Consensus over {len(responses)} runs: {consensus_label}")

    return Attribution(
        journey_code=journey.journey_code,
        label=consensus_label,
        interval=interval,
        posterior={consensus_label: round(avg_conf, 4)},
        rationale_text=f"Baseline B4 (LLM Judge): {rationale} (consensus {counter[consensus_label]}/{len(responses)})",
    )
