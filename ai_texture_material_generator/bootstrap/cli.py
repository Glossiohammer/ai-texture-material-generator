"""Headless CLI entry: batch-generate material sets from a prompt file."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ai_texture_material_generator.config.settings import load_settings
from ai_texture_material_generator.handlers.generate_handler import GenerateHandler
from ai_texture_material_generator.adapters.backend_registry import BackendRegistry
from ai_texture_material_generator.services.generation_service import GenerationService
from ai_texture_material_generator.services.export_service import ExportService

app = typer.Typer(add_completion=False, help="AI texture / material generator (headless)")
console = Console()


@app.command()
def generate(
    prompt: str = typer.Option(..., "--prompt", "-p", help="Text prompt for the material"),
    out: Path = typer.Option(Path("output"), "--out", "-o"),
    resolution: int = typer.Option(1024, "--res", min=256, max=4096),
    maps: str = typer.Option("albedo,normal,roughness,metallic,ao,height"),
) -> None:
    settings = load_settings(Path.cwd() / "config" / "default.yaml")
    registry = BackendRegistry.from_settings(settings)
    handler = GenerateHandler(
        GenerationService(registry, settings), ExportService(settings)
    )
    result = handler.handle(
        prompt=prompt,
        resolution=resolution,
        maps=[m.strip() for m in maps.split(",") if m.strip()],
        out_dir=out,
    )
    console.print(f"[green]wrote {result.written} files to {result.out_dir}[/green]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()