"""Seamless tiling via wrap-aware overlap blending.

Given an HxWx3 image, blends the last `overlap` columns/rows with the
first `overlap` columns/rows using a cosine ramp so the material tiles
without visible seams. Idempotent: applying twice is a no-op.
"""

from __future__ import annotations

import numpy as np


def make_tileable(img: np.ndarray, overlap: int) -> np.ndarray:
    if overlap <= 0:
        return img
    h, w = img.shape[:2]
    if overlap >= w or overlap >= h:
        raise ValueError(f"overlap {overlap} must be smaller than image dims {h}x{w}")

    out = img.copy()
    ramp = _cosine_ramp(overlap).reshape(1, overlap, 1)

    # Horizontal seam
    left = out[:, :overlap, :]
    right = out[:, w - overlap:, :]
    out[:, :overlap, :] = left * ramp + right * (1.0 - ramp)
    out[:, w - overlap:, :] = out[:, :overlap, :]

    # Vertical seam
    ramp_v = _cosine_ramp(overlap).reshape(overlap, 1, 1)
    top = out[:overlap, :, :]
    bot = out[h - overlap:, :, :]
    out[:overlap, :, :] = top * ramp_v + bot * (1.0 - ramp_v)
    out[h - overlap:, :, :] = out[:overlap, :, :]

    return out.astype(np.float32)


def _cosine_ramp(n: int) -> np.ndarray:
    t = np.linspace(0.0, 1.0, n, dtype=np.float32)
    return 0.5 - 0.5 * np.cos(np.pi * t)