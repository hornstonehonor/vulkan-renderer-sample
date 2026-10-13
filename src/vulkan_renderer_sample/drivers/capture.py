"""Output driver: dump raw frames to disk for offline diffing.

Writes one `.raw` (RGBA8) + one `.json` (frame metadata) per captured
frame into the configured directory. Not enabled by default.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from vulkan_renderer_sample.utils.logging import get_logger

log = get_logger("driver.capture")


class CaptureDriver:
    def __init__(self, out_dir: Path, every_n: int = 30) -> None:
        self._dir = out_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._every = every_n

    def maybe_capture(self, frame_index: int, pixels: np.ndarray,
                      meta: dict[str, object]) -> Path | None:
        if frame_index % self._every != 0:
            return None
        stamp = time.strftime("%Y%m%dT%H%M%S")
        stem = f"frame_{frame_index:06d}_{stamp}"
        raw = self._dir / f"{stem}.raw"
        # np.ndarray is (H, W, 4) uint8, tightly packed.
        raw.write_bytes(pixels.tobytes(order="C"))
        (self._dir / f"{stem}.json").write_text(
            json.dumps({"frame": frame_index, **meta}, indent=2), encoding="utf-8"
        )
        log.info("captured", path=str(raw))
        return raw