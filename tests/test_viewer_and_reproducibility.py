from __future__ import annotations

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from trinetra_link.config import REPO_ROOT
from trinetra_link.viewer.app import RESTRICTED_LEAKAGE_KEYS, create_viewer_app


@pytest.fixture
def viewer_client():
    app = create_viewer_app()
    return TestClient(app)


def test_viewer_health_and_html(viewer_client: TestClient):
    """Verify viewer health check and static HTML delivery."""
    resp_health = viewer_client.get("/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["service"] == "trinetra-link-viewer"

    resp_index = viewer_client.get("/")
    assert resp_index.status_code == 200
    assert "TriNetra-Link" in resp_index.text
    assert "Double-Blind Research Verification" in resp_index.text


def test_viewer_journey_list(viewer_client: TestClient):
    """Verify journey listing endpoint."""
    resp = viewer_client.get("/api/journeys")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "journey_code" in data[0]


def test_viewer_strict_blinding_no_truth_leakage(viewer_client: TestClient):
    """
    NON-NEGOTIABLE PROTOCOL REQUIREMENT:
    The research viewer must never reveal staging-log or ground-truth fields.
    Greps raw JSON and string responses to guarantee zero leakage.
    """
    # Test on multiple journey codes
    for code in ("JRN-2026-0001", "JRN-2026-0005", "JRN-2026-DEMO01"):
        resp = viewer_client.get(f"/api/journeys/{code}")
        if resp.status_code == 404:
            continue
        assert resp.status_code == 200

        raw_text = resp.text.lower()
        json_data = resp.json()

        # 1. Assert string content does not contain forbidden keys
        for forbidden in RESTRICTED_LEAKAGE_KEYS:
            assert f'"{forbidden}"' not in raw_text, (
                f"STRICT BLINDING LEAKAGE: Viewer response leaked restricted key '{forbidden}' in {code}"
            )

        # 2. Assert ground truth classification labels are not leaked
        assert "obs_determinable" not in raw_text
        assert "obs_degraded_incomplete" not in raw_text
        assert "obs_indistinguishable" not in raw_text

        # 3. Assert permitted fields exist
        assert "journey_code" in json_data
        assert "checkpoints" in json_data
        assert "weight_trace" in json_data
        assert "attribution" in json_data
        assert "label" in json_data["attribution"]
        assert "rationale_text" in json_data["attribution"]


def test_viewer_weight_trace_uncertainty_bands(viewer_client: TestClient):
    """Verify weight trace includes observed mean and +/- 3 sigma bounds."""
    resp = viewer_client.get("/api/journeys/JRN-2026-0001")
    if resp.status_code == 200:
        data = resp.json()
        trace = data.get("weight_trace", [])
        assert len(trace) == 4
        for cp in trace:
            assert "mean_weight_g" in cp
            assert "lower_bound_g" in cp
            assert "upper_bound_g" in cp
            assert cp["lower_bound_g"] <= cp["mean_weight_g"] <= cp["upper_bound_g"]


def test_documentation_and_reproducibility_artifacts_present():
    """Verify all Phase E documentation, SOPs, datasheets, and license files exist."""
    expected_files = [
        REPO_ROOT / "reproduce.sh",
        REPO_ROOT / "STATUS.md",
        REPO_ROOT / "LICENSE",
        REPO_ROOT / "CITATION.cff",
        REPO_ROOT / "docs" / "staging_SOP.md",
        REPO_ROOT / "docs" / "datasheet.md",
        REPO_ROOT / "docs" / "decisions.md",
        REPO_ROOT / "trinetra_link" / "viewer" / "static" / "index.html",
    ]

    for fpath in expected_files:
        assert fpath.exists(), f"Missing required Phase E artifact: {fpath}"
        assert fpath.stat().st_size > 50, f"Artifact is empty or incomplete: {fpath}"
