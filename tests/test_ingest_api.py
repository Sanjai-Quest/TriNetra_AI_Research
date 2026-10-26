from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from trinetra_link.ingest.api import app, DEFAULT_DEV_TOKEN
from trinetra_link.store.database import Store


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = tmp_path / "test_ingest_store.sqlite"
    monkeypatch.setenv("TRINETRA_DB_PATH", str(test_db))
    monkeypatch.setenv("DEVICE_INGEST_TOKEN", DEFAULT_DEV_TOKEN)
    return TestClient(app)


def make_dummy_jpeg_bytes(width: int = 640, height: int = 480, color: tuple = (120, 120, 120)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_serve_capture_ui(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "TriNetra-Link" in res.text


def test_auth_protection_on_api(client):
    # Missing token -> 401
    res = client.post("/journeys", json={"journey_code": "JRN-AUTH-01"})
    assert res.status_code == 401

    # Invalid token -> 401
    res_bad = client.post(
        "/journeys",
        json={"journey_code": "JRN-AUTH-01"},
        headers={"X-Device-Token": "wrong-token"},
    )
    assert res_bad.status_code == 401


def test_journey_creation_and_idempotency(client):
    headers = {"X-Device-Token": DEFAULT_DEV_TOKEN}

    # 1. Successful creation
    res = client.post(
        "/journeys",
        json={"journey_code": "JRN-INGEST-01", "metadata": {"test": True}},
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["status"] == "created"

    # 2. Idempotent re-post
    res_dup = client.post(
        "/journeys",
        json={"journey_code": "JRN-INGEST-01", "metadata": {"test": True}},
        headers=headers,
    )
    assert res_dup.status_code == 200
    assert res_dup.json()["status"] == "exists"


def test_checkpoint_sequence_violation_enforcement(client):
    headers = {"X-Device-Token": DEFAULT_DEV_TOKEN}
    img_bytes = make_dummy_jpeg_bytes()

    # Attempting to ingest CP2 when CP1 doesn't exist must fail
    meta = {
        "device_id": "DEV-01",
        "operator_id": "OP-01",
        "weights_g": [500.0, 500.1, 500.0],
    }
    files = [("files", ("cp2_front.jpg", img_bytes, "image/jpeg"))]
    data_form = {"data": json.dumps(meta)}

    res = client.post(
        "/journeys/JRN-SEQ-01/checkpoints/2",
        data=data_form,
        files=files,
        headers=headers,
    )
    assert res.status_code == 400
    assert "Sequence violation" in res.json()["detail"]


def test_checkpoint_upload_and_sha256_verification(client):
    headers = {"X-Device-Token": DEFAULT_DEV_TOKEN}
    img_bytes = make_dummy_jpeg_bytes(width=800, height=600)
    actual_hash = hashlib.sha256(img_bytes).hexdigest()

    # 1. Correct hash provided by client
    meta_good = {
        "device_id": "DEV-01",
        "operator_id": "OP-01",
        "weights_g": [350.0, 350.1, 350.0],
        "scale_id": "SCALE-01",
        "scale_status": "OK",
        "seal_qr": "SEAL-A01",
        "serial": "SN-A01",
        "client_hashes": {"cp1_front.jpg": actual_hash},
    }
    files_good = [("files", ("cp1_front.jpg", img_bytes, "image/jpeg"))]
    res_good = client.post(
        "/journeys/JRN-HASH-01/checkpoints/1",
        data={"data": json.dumps(meta_good)},
        files=files_good,
        headers=headers,
    )
    assert res_good.status_code == 201
    res_data = res_good.json()
    assert res_data["status"] == "success"
    assert res_data["quality_report"]["q_k"] > 0.0

    # 2. Hash mismatch intentional corruption test
    meta_bad = {
        "device_id": "DEV-01",
        "operator_id": "OP-01",
        "weights_g": [350.0, 350.1, 350.0],
        "client_hashes": {"cp1_front.jpg": "0000000000000000000000000000000000000000000000000000000000000000"},
    }
    files_bad = [("files", ("cp1_front.jpg", img_bytes, "image/jpeg"))]
    res_bad = client.post(
        "/journeys/JRN-HASH-02/checkpoints/1",
        data={"data": json.dumps(meta_bad)},
        files=files_bad,
        headers=headers,
    )
    assert res_bad.status_code == 400
    assert "Hash mismatch" in res_bad.json()["detail"]


def test_full_cp1_to_cp2_lifecycle_and_reconciliation(client):
    headers = {"X-Device-Token": DEFAULT_DEV_TOKEN}
    code = "JRN-LIFE-01"

    # CP1: Ingest origin baseline
    img1 = make_dummy_jpeg_bytes()
    meta1 = {
        "device_id": "DEV-01",
        "operator_id": "OP-01",
        "weights_g": [500.0, 500.1, 500.0],
        "scale_id": "SCALE-01",
        "scale_status": "OK",
        "seal_qr": "SEAL-ORIG-01",
        "serial": "SN-001",
    }
    res1 = client.post(
        f"/journeys/{code}/checkpoints/1",
        data={"data": json.dumps(meta1)},
        files=[("files", ("cp1_front.jpg", img1, "image/jpeg"))],
        headers=headers,
    )
    assert res1.status_code == 201
    assert res1.json()["reconcile_result"] is None  # CP1 has no baseline prior

    # CP2: Ingest with tamper (seal mismatch + weight loss)
    img2 = make_dummy_jpeg_bytes()
    meta2 = {
        "device_id": "DEV-02",
        "operator_id": "OP-02",
        "weights_g": [420.0, 420.0, 420.1],  # 80g loss
        "scale_id": "SCALE-02",
        "scale_status": "OK",
        "seal_qr": "SEAL-TAMPERED-02",        # Tampered seal
        "serial": "SN-001",
    }
    res2 = client.post(
        f"/journeys/{code}/checkpoints/2",
        data={"data": json.dumps(meta2)},
        files=[("files", ("cp2_front.jpg", img2, "image/jpeg"))],
        headers=headers,
    )
    assert res2.status_code == 201
    data2 = res2.json()
    reconcile = data2["reconcile_result"]
    assert reconcile is not None
    assert reconcile["fused_state"] == "ANOM"
    assert reconcile["weight_anomaly"] is True
    assert reconcile["identity_anomaly"] is True

    # Retrieve journey timeline
    res_get = client.get(f"/journeys/{code}", headers=headers)
    assert res_get.status_code == 200
    journey_data = res_get.json()
    assert journey_data["checkpoints_count"] == 2
    assert len(journey_data["journey"]["checkpoints"]) == 2
