"""RenderCommand — the unit flowing through the ingest pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RenderCommand:
    op: str
    args: dict[str, Any] = field(default_factory=dict)
    needs_barrier: bool = False

    def __post_init__(self) -> None:
        if not self.op:
            raise ValueError("RenderCommand.op must be non-empty")