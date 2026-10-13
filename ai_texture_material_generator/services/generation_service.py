"""Orchestrates a full material generation pass.

Flow:
  prompt -> backend.synthesize(albedo) -> derive height -> derive normal
         -> derive roughness/metallic/ao -> assemble MaterialSet

Derivation is deterministic given (albedo, seed), so re-running with the
same seed reproduces byte-identical maps.
"""

from __future__ import annotations

import hashlib

import numpy as np

from ai_texture_material_generator.adapters.backend_registry import BackendRegistry
from ai_texture_material_generator.config.settings import AppSettings
from ai_texture_material_generator.models.material import MapKind, MaterialSet, TextureMap
from ai_texture_material_generator.services.tiling_service import make_tileable
from ai_texture_material_generator.services.pbr_service import derive_pbr_maps


class GenerationService:
    def __init__(self, registry: BackendRegistry, settings: AppSettings) -> None:
        self._registry = registry
        self._settings = settings

    def generate(
        self,
        prompt: str,
        resolution: int,
        kinds: list[MapKind],
        seed: int | None = None,
    ) -> MaterialSet:
        if seed is None:
            seed = int.from_bytes(hashlib.sha256(prompt.encode()).digest()[:4], "little")

        backend = self._registry.resolve()
        albedo = backend.synthesize(prompt, resolution, seed)
        albedo = make_tileable(albedo, overlap=self._settings.model.tile_size // 8)

        name = _slug(prompt)
        material = MaterialSet(name=name, seed=seed, prompt=prompt)
        material.add(TextureMap(MapKind.ALBEDO, albedo, srgb=self._settings.export.srgb_albedo))

        derived = derive_pbr_maps(albedo, wanted=kinds)
        for kind, pixels in derived.items():
            material.add(TextureMap(kind, pixels, srgb=False))

        return material


def _slug(prompt: str) -> str:
    keep = [c if c.isalnum() else "_" for c in prompt.lower()]
    slug = "".join(keep).strip("_")
    return slug[:48] or "material"