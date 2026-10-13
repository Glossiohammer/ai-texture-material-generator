"""Selects and instantiates the diffusion backend at runtime.

Resolution order when backend == auto:
  1. torch.cuda.is_available() and VRAM >= 6GB  -> CudaBackend
  2. onnxruntime providers include CUDA         -> OnnxBackend
  3. otherwise                                  -> CpuBackend

Backends are singletons per process; the model is loaded once and kept
resident so repeated generations in one session don't pay load cost.
"""

from __future__ import annotations

from typing import Protocol

from ai_texture_material_generator.config.settings import AppSettings
from ai_texture_material_generator.models.material import Backend


class DiffusionBackend(Protocol):
    name: str

    def load(self) -> None: ...
    def synthesize(self, prompt: str, resolution: int, seed: int) -> "object": ...
    def unload(self) -> None: ...


class BackendRegistry:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._backend: DiffusionBackend | None = None

    @classmethod
    def from_settings(cls, settings: AppSettings) -> "BackendRegistry":
        return cls(settings)

    def resolve(self) -> DiffusionBackend:
        if self._backend is not None:
            return self._backend

        requested = Backend(self._settings.model.backend)
        if requested is Backend.AUTO:
            requested = self._auto_pick()

        self._backend = self._instantiate(requested)
        self._backend.load()
        return self._backend

    def _auto_pick(self) -> Backend:
        try:
            import torch  # noqa: PLC0415
            if torch.cuda.is_available():
                vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
                if vram_gb >= 6.0:
                    return Backend.CUDA
        except ImportError:
            pass

        try:
            import onnxruntime as ort  # noqa: PLC0415
            if "CUDAExecutionProvider" in ort.get_available_providers():
                return Backend.ONNX
        except ImportError:
            pass

        return Backend.CPU

    def _instantiate(self, backend: Backend) -> DiffusionBackend:
        from ai_texture_material_generator.adapters.cuda_backend import CudaBackend
        from ai_texture_material_generator.adapters.cpu_backend import CpuBackend
        from ai_texture_material_generator.adapters.onnx_backend import OnnxBackend

        weights = self._settings.model.weights_dir
        match backend:
            case Backend.CUDA:
                return CudaBackend(weights, self._settings.model)
            case Backend.ONNX:
                return OnnxBackend(weights, self._settings.model)
            case _:
                return CpuBackend(weights, self._settings.model)