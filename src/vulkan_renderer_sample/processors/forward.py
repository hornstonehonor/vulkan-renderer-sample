"""Forward pass processor.

Single-pass lighting. Cheapest path in the sample; the reference for
everything the deferred pass is compared against in tests.
"""
from __future__ import annotations

from vulkan_renderer_sample.models.commands import RenderCommand
from vulkan_renderer_sample.models.targets import RenderTarget


class ForwardPass:
    name = "forward"
    writes_to = ("color", "depth")
    reads_from: tuple[str, ...] = ()

    def __init__(self, target: RenderTarget) -> None:
        self._target = target

    def record(self) -> list[RenderCommand]:
        return [
            RenderCommand(op="begin_pass", args={"pass": self.name}),
            RenderCommand(op="bind_pipeline", args={"pipeline": "forward"}),
            RenderCommand(op="draw", args={"index_count": self._target.index_count}),
            RenderCommand(op="end_pass", args={"pass": self.name}),
        ]