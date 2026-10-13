"""Output driver: acquire -> present swapchain image.

Backpressure: if acquire returns OUT_OF_DATE the driver recreates the
swapchain and returns `PresentResult.RECREATED`. Callers must re-record
the frame.
"""
from __future__ import annotations

from enum import Enum, auto

from vulkan_renderer_sample.models.handles import SwapchainHandle
from vulkan_renderer_sample.utils.logging import get_logger

log = get_logger("driver.present")


class PresentResult(Enum):
    PRESENTED = auto()
    RECREATED = auto()
    SKIPPED = auto()


class PresentDriver:
    def __init__(self, swapchain: SwapchainHandle, vsync: bool = True) -> None:
        self._swapchain = swapchain
        self._vsync = vsync

    def present(self, frame_index: int) -> PresentResult:
        image = self._swapchain.acquire(timeout_ns=1_000_000_000)
        if image is None:
            log.warn("acquire_timeout", frame=frame_index)
            return PresentResult.SKIPPED
        if self._swapchain.needs_recreate:
            self._swapchain.recreate()
            return PresentResult.RECREATED
        self._swapchain.present(image)
        return PresentResult.PRESENTED