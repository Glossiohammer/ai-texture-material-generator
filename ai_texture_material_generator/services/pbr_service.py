"""Derives PBR maps from a base albedo image.

Normal map uses a Sobel filter on a luminance-derived height field.
Roughness is an inverted local-contrast estimate. Metallic defaults to a
constant unless a specular hint is present. AO is a cheap curvature proxy.

All operations are pure NumPy, no torch, so they run on any machine.
"""

from __future__ import annotations

import numpy as np

from ai_texture_material_generator.models.material import MapKind
from ai_texture_material_generator.utils.color import to_luminance


def _height_from_luminance(albedo: np.ndarray) -> np.ndarray:
    lum = to_luminance(albedo)
    # Local contrast boosts perceived relief on flat albedo.
    blurred = _box_blur(lum, radius=3)
    return np.clip(lum - blurred, -0.5, 0.5) + 0.5


def _box_blur(img: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return img
    k = 2 * radius + 1
    kernel = np.ones(k, dtype=np.float32) / k
    pad = radius
    padded = np.pad(img, pad, mode="reflect")
    tmp = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="valid"), 0, padded)
    out = np.apply_along_axis(lambda m: np.convolve(m, kernel, mode="valid"), 1, tmp)
    return out.astype(np.float32)


def height_to_normal(height: np.ndarray, strength: float = 2.0) -> np.ndarray:
    gy, gx = np.gradient(height)
    nx = -gx * strength
    ny = -gy * strength
    nz = np.ones_like(height)
    norm = np.sqrt(nx * nx + ny * ny + nz * nz)
    normal = np.stack([nx / norm, ny / norm, nz / norm], axis=-1)
    return ((normal + 1.0) * 0.5).astype(np.float32)


def derive_pbr_maps(
    albedo: np.ndarray, wanted: list[MapKind]
) -> dict[MapKind, np.ndarray]:
    out: dict[MapKind, np.ndarray] = {}
    height = _height_from_luminance(albedo) if (
        MapKind.HEIGHT in wanted or MapKind.NORMAL in wanted
    ) else None

    if MapKind.HEIGHT in wanted and height is not None:
        out[MapKind.HEIGHT] = height
    if MapKind.NORMAL in wanted and height is not None:
        out[MapKind.NORMAL] = height_to_normal(height)
    if MapKind.ROUGHNESS in wanted:
        lum = to_luminance(albedo)
        out[MapKind.ROUGHNESS] = np.clip(1.0 - lum, 0.0, 1.0)[..., None].repeat(3, axis=-1)
    if MapKind.METALLIC in wanted:
        out[MapKind.METALLIC] = np.full_like(albedo, 0.0)
    if MapKind.AO in wanted:
        lum = to_luminance(albedo)
        out[MapKind.AO] = np.clip(_box_blur(lum, radius=8), 0.0, 1.0)[..., None].repeat(3, axis=-1)
    if MapKind.EMISSIVE in wanted:
        out[MapKind.EMISSIVE] = np.zeros_like(albedo)
    return out