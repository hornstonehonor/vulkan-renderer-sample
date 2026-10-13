# Contributing to vulkan-renderer-sample

Thanks for wanting to push pixels. This repo is a **Vulkan renderer sample** — a
pipeline/worker style reference renderer in Python with optional native
accelerators (C++/C#/Java in scope) for shader compilation and validation.

## Ground rules

- Target Vulkan **1.3** (core) with optional **1.4** extensions behind feature flags.
- Every PR must run on `--backend=mock` without a GPU. CI runs headless on lavapipe.
- Shader changes require a regenerated SPIR-V blob in the same commit *or* a note
  in the PR body explaining the offline build.
- No vendor-specific workarounds unless gated behind `capabilities.features`.

## Development setup

```bash
git clone https://github.com/<org>/vulkan-renderer-sample.git
cd vulkan-renderer-sample
python -m venv .venv
. .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev,vulkan]"
python -m vulkan_renderer_sample --backend=mock --frames=120
```

## Pipeline / worker layout

This project is organized as a **pipeline**: ingest handlers feed processors,
processors emit into output drivers, and job utilities schedule the whole thing.

```
src/vulkan_renderer_sample/
  ingest/       # command buffers, descriptor sets, vertex streams
  processors/   # render passes (forward, deferred, post)
  drivers/      # swapchain present, offscreen capture
  jobs/         # frame graph scheduler, worker pool
  models/       # typed handles: Device, Image, Pipeline
  services/     # shader compile, validation, capability probe
  utils/        # math, logging, timing
  config/       # defaults, presets, feature flags
```

## Commit conventions

`<scope>: <imperative summary>` — e.g. `processors/deferred: fix G-buffer normals`.

## Tests

```bash
pytest -q
pytest -q -m "not gpu"
```

## Reporting issues

Include: OS, driver version (`vulkaninfo --summary`), GPU, and the JSON frame
trace from `logs/`.