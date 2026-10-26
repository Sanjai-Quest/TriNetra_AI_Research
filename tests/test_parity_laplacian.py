from __future__ import annotations

import numpy as np
import pytest
from trinetra_link.quality.features import compute_laplacian_variance_kotlin


def test_parity_laplacian_constant_image():
    # Constant image has 0 gradient everywhere, so rawVariance = 0.0 -> normalized = 0.0 -> clamped to 0.05
    img = np.full((100, 100), 128, dtype=np.uint8)
    var = compute_laplacian_variance_kotlin(img)
    assert var == 0.05


def test_parity_laplacian_manual_small_matrix():
    # Construct a 4x4 grayscale array
    # center pixels: (1,1), (1,2), (2,1), (2,2)
    img = np.array([
        [10, 20, 30, 40],
        [50, 60, 70, 80],
        [90, 100, 110, 120],
        [130, 140, 150, 160]
    ], dtype=np.uint8)

    # Let's hand calculate:
    # Kernel: top + bottom + left + right - 4 * center
    # For (1,1): center=60, top=20, bottom=100, left=50, right=70 -> 20 + 100 + 50 + 70 - 240 = 0
    # For (1,2): center=70, top=30, bottom=110, left=60, right=80 -> 30 + 110 + 60 + 80 - 280 = 0
    # Linear ramp across entire matrix means Laplacian is 0 everywhere!
    var = compute_laplacian_variance_kotlin(img)
    assert var == 0.05  # clamped to floor 0.05


def test_parity_laplacian_high_frequency_checkerboard():
    # Checkerboard pattern produces strong Laplacian variance
    img = np.zeros((64, 64), dtype=np.uint8)
    img[::2, ::2] = 255
    img[1::2, 1::2] = 255

    var = compute_laplacian_variance_kotlin(img)
    # High frequency texture must saturate upper bound 0.95
    assert var > 0.80
