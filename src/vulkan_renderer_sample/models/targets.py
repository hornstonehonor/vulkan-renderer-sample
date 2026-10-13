"""Render targets — the images a pass writes into."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RenderTarget:
    name: str
    width: int
    height: int
    index_count: int = 0
    vertex_count: int = 0

    @property
    def aspect(self) -> float:
        return self.width / self.height if self.height else 0.0