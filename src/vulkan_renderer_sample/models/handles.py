"""Opaque GPU handle models. These are handles, not wrappers — they carry
an id and a shape, nothing else. The device service owns lifetime.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ImageHandle:
    id: int
    width: int
    height: int
    format: str = "VK_FORMAT_R8G8B8A8_UNORM"


@dataclass(slots=True, frozen=True)
class BufferHandle:
    id: int
    size: int
    usage: str = "VK_BUFFER_USAGE_VERTEX_BUFFER_BIT"


@dataclass(slots=True)
class SwapchainHandle:
    id: int
    width: int
    height: int
    image_count: int = 3
    needs_recreate: bool = False

    def acquire(self, timeout_ns: int) -> ImageHandle | None:
        raise NotImplementedError("backed by the device service at runtime")

    def present(self, image: ImageHandle) -> None:
        raise NotImplementedError("backed by the device service at runtime")

    def recreate(self) -> None:
        self.needs_recreate = False