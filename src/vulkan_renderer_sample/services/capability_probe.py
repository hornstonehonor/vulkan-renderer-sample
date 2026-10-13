"""Capability probe: read what the loader/ICD actually reports.

Failure mode: on boxes without a loader, `probe()` returns a Capabilities
with `has_gpu=False` and `backend="mock"` rather than raising. The
scheduler only refuses to run when the caller explicitly asked for `gpu`.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass

from vulkan_renderer_sample.config.defaults import RendererConfig
from vulkan_renderer_sample.utils.logging import get_logger

log = get_logger("capability")


@dataclass(slots=True)
class Capabilities:
    has_gpu: bool
    backend: str
    api_version: str = "1.3.0"
    device_name: str = "mock"
    driver_version: str = "0.0.0"
    supports_ray_query: bool = False


class CapabilityProbe:
    def __init__(self, cfg: RendererConfig) -> None:
        self._cfg = cfg

    def probe(self) -> Capabilities:
        if self._cfg.backend == "mock":
            return Capabilities(has_gpu=False, backend="mock")
        loader = shutil.which("vulkaninfo")
        if loader is None:
            log.warn("no_loader_found", falling_back="mock")
            return Capabilities(has_gpu=False, backend="mock")
        # A real probe parses `vulkaninfo --summary`; kept out of the sample
        # path so CI doesn't shell out.
        return Capabilities(has_gpu=True, backend="gpu", device_name="probed-device")