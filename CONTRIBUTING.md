# Contributing to ai-texture-material-generator

Thanks for wanting to push pixels and parameters. This repo is a Windows
desktop tool for turning text prompts, reference photos, and heightmaps
into PBR-ready material sets (albedo, normal, roughness, metallic, AO,
height, emissive).

## Ground rules

- Python 3.11+ on Windows 10/11 (x64). CUDA optional but recommended
  for the diffusion backend.
- One feature per PR. Keep handlers thin — business logic belongs in
  `services/`, not in `handlers/`.
- Type hints everywhere. `mypy --strict` on `core/` and `services/`.
- No new runtime dependency without a note in the PR body explaining
  size, license, and why an existing dep can't do the job.

## Layout

```
ai_texture_material_generator/   # package root
  bootstrap/                     # app entry, DI wiring, cli
  handlers/                      # thin request handlers (no business logic)
  services/                      # business logic: generation, tiling, export
  models/                        # dataclasses, enums, schemas
  adapters/                      # platform + backend adapters (CUDA, CPU, ONNX)
  config/                        # settings, presets, paths
  utils/                         # color math, image io, logging
  ui/                            # PySide6 windows and widgets
tests/                           # pytest
scripts/                         # dev tooling
docs/                            # architecture notes
```

## Dev setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev,cuda]"
pytest -q
```

## Commit style

`service(tile): add wrap-aware seam blending`
`handler(generate): validate prompt length before dispatch`
`adapter(cuda): fall back to CPU when VRAM < 6GB`

## Reporting issues

Include: Windows build, GPU + driver, backend (`cuda`/`cpu`/`onnx`),
prompt used, output resolution, and the `logs/last_run.log` tail.