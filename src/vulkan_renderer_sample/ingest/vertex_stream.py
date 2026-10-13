"""Ingest handler: pack interleaved vertex attributes into a staging buffer.

Vertex layout (stride 32B):
    location 0 : vec3 position   (offset 0)
    location 1 : vec3 normal     (offset 12)
    location 2 : vec2 uv         (offset 24)
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

import numpy as np

VERTEX_STRIDE = 32
_LAYOUT = "<3f3f2f"


@dataclass(slots=True, frozen=True)
class Vertex:
    px: float
    py: float
    pz: float
    nx: float
    ny: float
    nz: float
    u: float
    v: float


class VertexStreamIngest:
    def __init__(self) -> None:
        self._buf = bytearray()

    def push(self, verts: list[Vertex]) -> None:
        for v in verts:
            self._buf += struct.pack(
                _LAYOUT, v.px, v.py, v.pz, v.nx, v.ny, v.nz, v.u, v.v
            )

    def as_numpy(self) -> np.ndarray:
        """Returns shape (N, 8) float32. Raises ValueError on misaligned buf."""
        if len(self._buf) % VERTEX_STRIDE != 0:
            raise ValueError(
                f"vertex buffer misaligned: {len(self._buf)} bytes "
                f"is not a multiple of {VERTEX_STRIDE}"
            )
        return np.frombuffer(bytes(self._buf), dtype=np.float32).reshape(-1, 8)

    def reset(self) -> None:
        self._buf.clear()