from __future__ import annotations

from datetime import datetime, timezone
import numpy as np
import pytest
from trinetra_link.reconcile.visual import (
    compute_visual_change_score,
    order_corner_points,
    rectify_surface_homography,
    reconcile_visual,
)
from trinetra_link.schema.models import CheckpointObservation, ImageRef


def test_order_corner_points():
    pts = np.array([[100, 100], [0, 0], [100, 0], [0, 100]], dtype="float32")
    ordered = order_corner_points(pts)
    assert np.allclose(ordered[0], [0, 0])      # top-left
    assert np.allclose(ordered[1], [100, 0])    # top-right
    assert np.allclose(ordered[2], [100, 100])  # bottom-right
    assert np.allclose(ordered[3], [0, 100])    # bottom-left


def test_homography_rectification_output_dimensions():
    img = np.full((300, 400, 3), 200, dtype=np.uint8)
    rect = rectify_surface_homography(img, target_dim=(256, 256))
    assert rect.shape == (256, 256, 3)


def test_homography_rectification_with_distinct_rectangle():
    # Synthetic image with a bright white box on dark background
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    img[50:350, 50:350] = 255
    rect = rectify_surface_homography(img, target_dim=(200, 200))
    assert rect.shape == (200, 200, 3)


def test_visual_change_score_identical_images():
    img = np.full((128, 128, 3), 150, dtype=np.uint8)
    img[20:60, 20:60] = 50
    score = compute_visual_change_score(img, img)
    assert score == 0.0


def test_visual_change_score_divergent_images():
    img_a = np.full((128, 128, 3), 255, dtype=np.uint8)
    img_b = np.full((128, 128, 3), 0, dtype=np.uint8)
    score = compute_visual_change_score(img_a, img_b)
    assert score > 0.50


def test_reconcile_visual_matching_and_divergent_observations():
    img_a = np.full((128, 128, 3), 180, dtype=np.uint8)
    img_a[20:80, 20:80] = 40

    img_b_match = img_a.copy()
    img_b_tamper = np.full((128, 128, 3), 10, dtype=np.uint8)

    obs_base = CheckpointObservation(
        journey_code="JRN-VIS-01",
        cp_index=1,
        ts_utc=datetime.now(timezone.utc),
        device_id="DEV-01",
        operator_id="OP-01",
        weights_g=[500.0, 500.0, 500.0],
        scale_id="SCALE-STD",
        scale_status="OK",
        images=[ImageRef(side="front", path="mock_a.png", sha256="h1", w=128, h=128)],
    )

    obs_curr = CheckpointObservation(
        journey_code="JRN-VIS-01",
        cp_index=2,
        ts_utc=datetime.now(timezone.utc),
        device_id="DEV-02",
        operator_id="OP-02",
        weights_g=[500.0, 500.0, 500.0],
        scale_id="SCALE-STD",
        scale_status="OK",
        images=[ImageRef(side="front", path="mock_b.png", sha256="h2", w=128, h=128)],
    )

    # 1. Matching images
    is_anom, scores = reconcile_visual(
        obs_base, obs_curr, visual_threshold=0.25,
        image_arrays_a={"front": img_a},
        image_arrays_b={"front": img_b_match},
    )
    assert not is_anom
    assert scores["front"] < 0.25

    # 2. Tampered images
    is_anom_t, scores_t = reconcile_visual(
        obs_base, obs_curr, visual_threshold=0.25,
        image_arrays_a={"front": img_a},
        image_arrays_b={"front": img_b_tamper},
    )
    assert is_anom_t
    assert scores_t["front"] > 0.25
