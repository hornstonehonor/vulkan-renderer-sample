"""Device service: open a logical device, expose handles, own lifetime.

In mock mode this returns a fully-functional stub so the scheduler can
run the whole ingest/process/present graph without a driver.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from vulkan_renderer_sample.config.defaults import RendererConfig
from vulkan_renderer_sample.ingest.command_buffer import CommandBatch
from vulkan_renderer_sample.models.handles import SwapchainHandle
from vulkan_renderer_sample.models.targets import RenderTarget
from vulkan_renderer_sample.services.capability_probe import Capabilities
from vulkan_renderer_sample.utils.logging import get_logger

log = get_logger("device")


@dataclass
class Device:
    backend: str
    swapchain: SwapchainHandle
    primary_target: RenderTarget
    submitted: int = 0
    _closed: bool = field(default=False, repr=False)

    def submit(self, batch: CommandBatch) -> None:
        # A real backend calls vkQueueSubmit here; the sample counts and
        # drops, which is enough to exercise the graph.
        self.submitted += batch.total()

    def window_should_close(self) -> bool:
        return self._closed

    def close(self) -> None:
        self._closed = True


def open_device(cfg: RendererConfig, caps: Capabilities) -> Device:
    swapchain = SwapchainHandle(id=1, width=cfg.width, height