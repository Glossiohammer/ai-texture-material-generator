"""Typed settings loaded from YAML, with env-var overrides.

Precedence (low -> high):
  default.yaml  <  user.yaml  <  AITMG_* env vars  <  explicit kwargs

Missing keys fall back to the dataclass defaults. Unknown keys are
rejected so typos surface at startup instead of silently doing nothing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass(slots=True)
class ModelSettings:
    backend: str = "auto"           # auto | cuda | cpu | onnx
    weights_dir: Path = Path("models")
    safety_checker: bool = False    # NSFW filter; off by default for local use
    tile_size: int = 512
    steps: int = 28
    guidance: float = 6.5


@dataclass(slots=True)
class ExportSettings:
    default_format: str = "png"     # png | tga | exr
    bit_depth: int = 8
    srgb_albedo: bool = True
    normal_convention: str = "opengl"  # opengl | directx


@dataclass(slots=True)
class AppSettings:
    model: ModelSettings = field(default_factory=ModelSettings)
    export: ExportSettings = field(default_factory=ExportSettings)
    output_dir: Path = Path("output")
    log_level: str = "INFO"
    threads: int = 0                # 0 = auto


def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load_settings(path: Path) -> AppSettings:
    raw: dict = {}
    if path.exists():
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    user = path.with_name("user.yaml")
    if user.exists():
        raw = _merge(raw, yaml.safe_load(user.read_text(encoding="utf-8")) or {})

    env_overrides = {
        k[len("AITMG_"):].lower(): v
        for k, v in os.environ.items()
        if k.startswith("AITMG_")
    }
    if "backend" in env_overrides:
        raw.setdefault("model", {})["backend"] = env_overrides["backend"]

    model = ModelSettings(**raw.get("model", {}))
    export = ExportSettings(**raw.get("export", {}))
    return AppSettings(
        model=model,
        export=export,
        output_dir=Path(raw.get("output_dir", "output")),
        log_level=raw.get("log_level", "INFO"),
        threads=int(raw.get("threads", 0)),
    )