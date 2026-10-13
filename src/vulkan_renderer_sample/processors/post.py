"""Post-processing chain processor: bloom -> tonemap -> resolve."""
from __future__ import annotations

from vulkan_renderer_sample.models.commands import RenderCommand


class PostPass:
    name = "post"
    writes_to = ("swapchain",)
    reads_from = ("color",)

    CHAIN = ("bloom_downsample", "bloom_upsample", "tonemap", "resolve")

    def record(self) -> list[RenderCommand]:
        cmds: list[RenderCommand] = []
        for stage in self.CHAIN:
            cmds.append(RenderCommand(op="bind_pipeline", args={"pipeline": stage}))
            cmds.append(RenderCommand(op="dispatch_or_draw", args={"stage": stage}))
        return cmds