"""Core domain types for a generated material set."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import numpy as np


class MapKind(str, Enum):
    ALBEDO = "albedo"
    NORMAL = "normal"
    ROUGHNESS = "roughness"
    METALLIC = "metallic"
    AO = "ao"
    HEIGHT = "height"
    EMISSIVE = "emissive"


class Backend(str, Enum):
    AUTO = "auto"
    CUDA = "cuda"
    CPU = "cpu"
    ONNX = "onnx"


@dataclass(slots=True)
class TextureMap:
    """A single channel map: HxWx3 float32 in [0,1] (or HxW for scalar maps)."""
    kind: MapKind
    pixels: np.ndarray
    srgb: bool = False

    def __post_init__(self) -> None:
        if self.pixels.dtype != np.float32:
            self.pixels = self.pixels.astype(np.float32)
        if self.pixels.ndim not in (2, 3):
            raise ValueError(f"{self.kind}: expected 2D or 3D array, got {self.pixels.ndim}D")

    @property
    def resolution(self) -> tuple[int, int]:
        h, w = self.pixels.shape[:2]
        return w, h


@dataclass(slots=True)
class MaterialSet:
    """A complete PBR material: one TextureMap per requested channel."""
    name: str
    maps: dict[MapKind, TextureMap] = field(default_factory=dict)
    seed: int = 0
    prompt: str = ""

    def add(self, tex: TextureMap) -> None:
        self.maps[tex.kind] = tex

    def has(self, kind: MapKind) -> bool:
        return kind in self.maps

    def write_paths(self, out_dir: Path) -> dict[MapKind, Path]:
        return {k: out_dir / f"{self.name}_{k.value}.png" for k in self.maps}