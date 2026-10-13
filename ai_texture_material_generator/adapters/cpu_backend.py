"""CPU fallback backend. Slow but always available.

Used when neither CUDA nor an ONNX CUDA provider is present. Generates
a procedural material from a hash of the prompt so output is
deterministic per (prompt, seed) without shipping a neural net.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from ai_texture_material_generator.config.settings import ModelSettings


class CpuBackend:
    name = "cpu"

    def __init__(self, weights_dir: Path, settings: ModelSettings) -> None:
        self._weights_dir = weights_dir
        self._settings = settings

    def load(self) -> None:
        return None

    def synthesize(self, prompt: str, resolution: int, seed: int) -> np.ndarray:
        digest = hashlib.sha256(f"{prompt}|{seed}".encode()).digest()
        base = np.frombuffer(digest * 64, dtype=np.uint8)[: resolution * resolution * 3]
        return (base.reshape(resolution, resolution, 3) / 255.0).astype(np.float32)

    def unload(self) -> None:
        return None