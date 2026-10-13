"""GUI bootstrap for ai-texture-material-generator.

Wires the dependency graph (settings -> services -> handlers -> UI) and
starts the Qt event loop. All heavy backends are resolved lazily so the
window paints before CUDA initializes.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ai_texture_material_generator.config.settings import load_settings
from ai_texture_material_generator.services.generation_service import GenerationService
from ai_texture_material_generator.services.export_service import ExportService
from ai_texture_material_generator.adapters.backend_registry import BackendRegistry
from ai_texture_material_generator.ui.main_window import MainWindow


def build_container() -> dict[str, object]:
    settings = load_settings(Path.cwd() / "config" / "default.yaml")
    registry = BackendRegistry.from_settings(settings)
    generation = GenerationService(registry, settings)
    export = ExportService(settings)
    return {"settings": settings, "registry": registry, "generation": generation, "export": export}


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("ai-texture-material-generator")
    container = build_container()
    window = MainWindow(container)  # type: ignore[arg-type]
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())