from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

from trinetra_link.schema.models import CheckpointObservation, ImageRef


def order_corner_points(pts: np.ndarray) -> np.ndarray:
    """Order coordinates: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def rectify_surface_homography(
    image: np.ndarray,
    corners: Optional[np.ndarray | List[List[float]]] = None,
    target_dim: Tuple[int, int] = (512, 512),
) -> np.ndarray:
    """
    Rectify parcel face using a 4-point homography projection.
    If corners are not specified, automatic corner contour detection is used,
    falling back to uniform full-frame scaling.
    """
    tw, th = target_dim
    dst_corners = np.array([
        [0, 0],
        [tw - 1, 0],
        [tw - 1, th - 1],
        [0, th - 1]
    ], dtype="float32")

    if corners is not None and len(corners) == 4:
        src_corners = order_corner_points(np.array(corners, dtype="float32"))
    else:
        # Automatic rectangular polygon detector
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best_quad = None
        max_area = 0.0
        h_img, w_img = gray.shape[:2]

        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            if len(approx) == 4:
                area = cv2.contourArea(approx)
                if area > 0.2 * (h_img * w_img) and area > max_area:
                    max_area = area
                    best_quad = approx.reshape(4, 2)

        if best_quad is not None:
            src_corners = order_corner_points(best_quad.astype("float32"))
        else:
            # Fallback to entire image frame
            src_corners = np.array([
                [0, 0],
                [w_img - 1, 0],
                [w_img - 1, h_img - 1],
                [0, h_img - 1]
            ], dtype="float32")

    M = cv2.getPerspectiveTransform(src_corners, dst_corners)
    rectified = cv2.warpPerspective(image, M, (tw, th))
    return rectified


def compute_visual_change_score(
    image_a: np.ndarray,
    image_b: np.ndarray,
    corners_a: Optional[np.ndarray | List[List[float]]] = None,
    corners_b: Optional[np.ndarray | List[List[float]]] = None,
) -> float:
    """
    Compute change score from structural dissimilarity: 1.0 - SSIM.
    Values range from 0.0 (identical structure) to 1.0 (complete divergence).
    """
    rect_a = rectify_surface_homography(image_a, corners_a)
    rect_b = rectify_surface_homography(image_b, corners_b)

    gray_a = cv2.cvtColor(rect_a, cv2.COLOR_BGR2GRAY) if rect_a.ndim == 3 else rect_a
    gray_b = cv2.cvtColor(rect_b, cv2.COLOR_BGR2GRAY) if rect_b.ndim == 3 else rect_b

    similarity = float(ssim(gray_a, gray_b))
    change_score = float(np.clip(1.0 - similarity, 0.0, 1.0))
    return round(change_score, 4)


def reconcile_visual(
    obs_baseline: CheckpointObservation,
    obs_current: CheckpointObservation,
    visual_threshold: float = 0.25,
    image_arrays_a: Optional[Dict[str, np.ndarray]] = None,
    image_arrays_b: Optional[Dict[str, np.ndarray]] = None,
) -> Tuple[bool, Dict[str, float]]:
    """
    Multimodal visual surface reconciliation across corresponding package faces.
    Returns (is_visual_anomaly, per_side_change_scores).
    """
    side_scores: Dict[str, float] = {}
    is_anomaly = False

    # Map side -> ImageRef
    images_a = {img.side: img for img in obs_baseline.images}
    images_b = {img.side: img for img in obs_current.images}

    common_sides = set(images_a.keys()).intersection(images_b.keys())
    if not common_sides:
        return False, {}

    for side in common_sides:
        arr_a = image_arrays_a.get(side) if image_arrays_a else None
        arr_b = image_arrays_b.get(side) if image_arrays_b else None

        if arr_a is None and Path(images_a[side].path).exists():
            arr_a = cv2.imread(str(images_a[side].path))
        if arr_b is None and Path(images_b[side].path).exists():
            arr_b = cv2.imread(str(images_b[side].path))

        if arr_a is not None and arr_b is not None:
            score = compute_visual_change_score(arr_a, arr_b)
            side_scores[side] = score
            if score > visual_threshold:
                is_anomaly = True

    return is_anomaly, side_scores
