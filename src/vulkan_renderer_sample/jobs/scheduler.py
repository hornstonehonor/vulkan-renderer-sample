"""Frame graph scheduler.

Per frame: ingest -> process -> present. Runs the whole graph against a
mock device when no real device is available, which is how CI exercises
this sample without a GPU.
"""
from __future__ import annotations

from vulkan_renderer_sample.config.defaults import RendererConfig
from vulkan_renderer_sample.drivers.present import PresentDriver, PresentResult
from vulkan_renderer_sample.ingest.command_buffer import CommandBufferIngest
from vulkan_renderer_sample.processors.forward import ForwardPass
from vulkan_renderer_sample.processors.post import PostPass
from vulkan_renderer_sample.services.capability_probe import Capabilities
from vulkan_renderer_sample.services.device import open_device
from vulkan_renderer_sample.utils.logging import get_logger

log = get_logger("scheduler")


class FrameScheduler:
    def __init__(self, cfg: RendererConfig, caps: Capabilities) -> None:
        self._cfg = cfg
        self._caps = caps
        self._device = open_device(cfg, caps)
        self._ingest = CommandBufferIngest()
        self._present = PresentDriver(self._device.swapchain, vsync=cfg.vsync)

    def _build_pass_chain(self):
        target = self._device.primary_target
        if self._cfg.preset == "deferred":
            from vulkan_renderer_sample.processors.deferred import DeferredPass
            chain = [DeferredPass(target)]
        else:
            chain = [ForwardPass(target)]
        chain.append(PostPass())
        return chain

    def run(self) -> None:
        chain = self._build_pass_chain()
        log.info("pass_chain", chain=[p.name for p in chain])
        frame = 0
        limit = self._cfg.frames or 10**9
        while frame < limit and not self._device.window_should_close():
            commands = [c for p in chain for c in p.record()]
            batch = self._ingest.ingest(commands)
            self._device.submit(batch)
            result = self._present.present(frame)
            if result is PresentResult.RECREATED:
                log.warn("swapchain_recreated", frame=frame)
                continue
            frame += 1
        log.info("shutdown", frames=frame)