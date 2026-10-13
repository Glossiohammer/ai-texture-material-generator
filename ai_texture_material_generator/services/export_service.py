"""Writes a MaterialSet to disk as image files.

Handles sRGB vs linear encoding, 8/16-bit output, and DirectX vs OpenGL
normal-map green channel flipping. Returns the number of files written.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from ai_texture_material_generator.config.settings import AppSettings
from ai_texture_material_generator.models.material import MapKind, MaterialSet, TextureMap


class ExportService:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def write_material(self, material: MaterialSet, out_dir: Path) -> int:
        out_dir.mkdir(parents=True, exist_ok=True)
        written = 0
        for kind, tex in material.maps.items():
            path = out_dir / f"{material.name}_{kind.value}.{self._settings.export.default_format}"
            self._write_map(tex, path)
            written += 1
        return written

    def _write_map(self, tex: TextureMap, path: Path) -> None:
        pixels = tex.pixels
        if tex.kind is MapKind.NORMAL and self._settings.export.normal_convention == "directx":
            pixels = pixels.copy()
            pixels[..., 1] = 1.0 - pixels[..., 1]

        if pixels.ndim == 2:
            pixels = np.stack([pixels] * 3, axis=-1)

        if self._settings.export.bit_depth == 16:
            arr = (np.clip(pixels, 0.0, 1.