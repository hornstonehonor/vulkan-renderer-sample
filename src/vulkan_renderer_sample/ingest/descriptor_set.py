"""Ingest handler: bind image/sampler/buffer handles to set indices.

Watch for: descriptor set 0 is reserved for per-frame uniforms in this
sample. Do not repurpose it; the scheduler assumes it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from vulkan_renderer_sample.models.handles import BufferHandle, ImageHandle


@dataclass(slots=True)
class Binding:
    set_index: int
    binding: int
    handle: ImageHandle | BufferHandle


class DescriptorSetIngest:
    RESERVED_FRAME_SET = 0

    def __init__(self) -> None:
        self._bindings: list[Binding] = []

    def bind(self, set_index: int, binding: int,
             handle: ImageHandle | BufferHandle) -> None:
        if set_index == self.RESERVED_FRAME_SET:
            raise ValueError("set 0 is reserved for per-frame uniforms")
        self._bindings.append(Binding(set_index, binding, handle))

    def flush(self) -> list[Binding]:
        out, self._bindings = self._bindings, []
        return out