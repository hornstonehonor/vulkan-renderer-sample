"""Ingest handler: accumulate recorded commands into a batch for submission.

Inputs:  a stream of `RenderCommand` records from processors.
Outputs: `CommandBatch` — an ordered, deduplicated set of submits.
Side effects: none (pure); the driver owns the actual vkQueueSubmit.

Complexity: O(n) over commands, O(k) merge over k bind states.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from vulkan_renderer_sample.models.commands import RenderCommand


@dataclass(slots=True)
class CommandBatch:
    submits: list[list[RenderCommand]] = field(default_factory=list)
    barriers: int = 0

    def total(self) -> int:
        return sum(len(s) for s in self.submits)


class CommandBufferIngest:
    """Coalesces commands into submission batches, inserting barriers where
    a pass changes image layout. A pass declaring `writes_to` that another
    pass later reads forces a barrier — do not remove this, it is the only
    synchronization the sample ships with."""

    def __init__(self, max_per_submit: int = 512) -> None:
        self._max = max_per_submit

    def ingest(self, commands: Iterable[RenderCommand]) -> CommandBatch:
        batch = CommandBatch()
        current: list[RenderCommand] = []
        for cmd in commands:
            if cmd.needs_barrier:
                batch.barriers += 1
            current.append(cmd)
            if len(current) >= self._max:
                batch.submits.append(current)
                current = []
        if current:
            batch.submits.append(current)
        return batch