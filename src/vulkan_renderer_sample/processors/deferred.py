"""Deferred pass processor: geometry -> G-buffer, then full-screen lighting.

Two sub-passes. The G-buffer is a fixed 4-attachment target; attachment 3
is the normal+roughness pack and must not change without updating
`shaders/lighting.frag`.
"""
from __future__ import annotations

from vulkan_renderer_sample.models.commands import RenderCommand
from vulkan_renderer_sample.models.targets import RenderTarget

GBUFFER_ATTACHMENTS = ("albedo", "position", "normal_rough", "velocity")


class DeferredPass:
    name = "deferred"
    writes_to = ("gbuffer", "color")
    reads_from = ("gbuffer",)

    def __init__(self, target: RenderTarget) -> None:
        self._target = target

    def record_geometry(self) -> list[RenderCommand]:
        cmds = [RenderCommand(op="begin_pass", args={"pass": "gbuffer"})]
        for att in GBUFFER_ATTACHMENTS:
            cmds.append(RenderCommand(op="bind_attachment", args={"name": att}))
        cmds.append(RenderCommand(op="bind_pipeline", args={"pipeline": "gbuffer"}))
        cmds.append(RenderCommand(op="draw", args={"index_count": self._target.index_count}))
        cmds.append(RenderCommand(op="end_pass", args={"pass": "gbuffer"}))
        return cmds

    def record_lighting(self) -> list[RenderCommand]:
        return [
            RenderCommand(op="begin_pass", args={"pass": "lighting"}),
            RenderCommand(op="bind_pipeline", args={"pipeline": "lighting"}),
            RenderCommand(op="draw", args={"vertex_count": 3}),
            RenderCommand(op="end_pass", args={"pass": "lighting"}),
        ]

    def record(self) -> list[RenderCommand]:
        # G-buffer writes are read by lighting: barrier is mandatory.
        cmds = self.record_geometry()
        cmds[-1] = RenderCommand(op="end_pass", args={"pass": "gbuffer"}, needs_barrier=True)
        return cmds + self.record_lighting()