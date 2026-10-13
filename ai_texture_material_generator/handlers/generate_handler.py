"""Handler for a single material generation request.

Thin: validates input, delegates to GenerationService + ExportService,
returns a result dataclass. No diffusion logic, no file IO beyond the
service calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_texture_material_generator.models.material import MapKind
from ai_texture_material_generator.services.generation_service import GenerationService
from ai_texture_material_generator.services.export_service import ExportService


@dataclass(slots=True)
class GenerateResult:
    out_dir: Path
    written: int
    maps: list[MapKind]


class GenerateHandler:
    def __init__(self, generation: GenerationService, export: ExportService) -> None:
        self._generation = generation
        self._export = export

    def handle(
        self,
        prompt: str,
        resolution: int,
        maps: list[str],
        out_dir: Path,
    ) -> GenerateResult:
        cleaned = prompt.strip()
        if not cleaned:
            raise ValueError("prompt must not be empty")
        if resolution < 256 or resolution > 4096:
            raise ValueError(f"resolution {resolution} out of range [256, 4096]")

        kinds = [MapKind(m) for m in maps]
        material = self._generation.generate(cleaned, resolution, kinds)
        written = self._export.write_material(material, out_dir)
        return GenerateResult(out_dir=out_dir, written=written, maps=list(material.maps.keys()))