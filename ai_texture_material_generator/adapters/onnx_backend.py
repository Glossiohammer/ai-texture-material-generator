"""ONNX Runtime backend. Uses the CUDAExecutionProvider when available.

Kept separate from CudaBackend so users without a torch install can
still run on GPU through onnxruntime-gpu.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ai_texture_material_generator.config.settings import ModelSettings


class OnnxBackend:
    name = "onnx"

    def __init__(self, weights_dir: Path, settings: ModelSettings) -> None:
        self._weights_dir = weights_dir
        self._settings = settings
        self._session = None

    def load(self) -> None:
        import onnxruntime as ort  # noqa: PLC0415
        model_path = self._weights_dir / "diffusion.onnx"
        if not model_path.exists():
            raise FileNotFoundError(
                f"ONNX weights missing at {model_path}. Run scripts/fetch_weights.py"
            )
        providers = ort.get_available_providers()
        self._session = ort.InferenceSession(str(model_path), providers=providers)

    def synthesize(self, prompt: str, resolution: int, seed: int) -> np.ndarray:
        if self._session is None:
            raise RuntimeError("OnnxBackend.load() must be called before synthesize()")
        rng = np.random.default_rng(seed)
        noise = rng.standard_normal((1, 4, resolution // 8, resolution // 8), dtype=np.float32)
        out = self._session.run(None, {"latent": noise})[0]
        rgb = out[0, :3].transpose(1, 2, 0)
        return np.clip(rgb, 0.0, 1.0).astype(np.float32)

    def unload(self) -> None:
        self._session = None