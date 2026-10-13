"""Bounded worker pool for async asset/shader jobs.

Not used for GPU submits (those are single-threaded by design in this
sample). Used for shader compile warmup and asset decoding.
"""
from __future__ import annotations

import concurrent.futures as cf
from collections.abc import Callable
from typing import Any


class WorkerPool:
    def __init__(self, size: int = 4) -> None:
        self._pool = cf.ThreadPoolExecutor(max_workers=size, thread_name_prefix="vrs")

    def map(self, fn: Callable[[Any], Any], items: list[Any]) -> list[Any]:
        return list(self._pool.map(fn, items))

    def shutdown(self, wait: bool = True) -> None:
        self._pool.shutdown(wait=wait)

    def __enter__(self) -> "WorkerPool":
        return self

    def __exit__(self, *exc: object) -> None:
        self.shutdown()