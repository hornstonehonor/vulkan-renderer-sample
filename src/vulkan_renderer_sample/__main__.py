"""Entry point.

Boots the renderer as a job: ingest -> process -> present. Everything the
renderer does is a pipeline stage or a worker task feeding a stage.

Runtime note: `--backend=mock` runs the full graph with a stub device so CI
and headless boxes can exercise the pipeline without a GPU.
"""
from __future__ import annotations

import argparse
import sys

from vulkan_renderer_sample.config.defaults import load_config
from vulkan_renderer_sample.jobs.scheduler import FrameScheduler
from vulkan_renderer_sample.services.capability_probe import CapabilityProbe
from vulkan_renderer_sample.utils.logging import configure_logging, get_logger


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vulkan-renderer-sample")
    p.add_argument("--backend", choices=("auto", "gpu", "mock"), default="auto")
    p.add_argument("--frames", type=int, default=0, help="0 = run until window closes")
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=720)
    p.add_argument("--preset", default="forward")
    p.add_argument("--validation", action="store_true")
    p.add_argument("--capture", metavar="DIR", default=None)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args)
    configure_logging(cfg.log_level)
    log = get_logger("boot")

    log.info("boot", backend=args.backend, preset=args.preset,
             resolution=(args.width, args.height), frames=args.frames)

    caps = CapabilityProbe(cfg).probe()
    if args.backend == "gpu" and not caps.has_gpu:
        log.error("no_vulkan_device", requested="gpu")
        return 2

    scheduler = FrameScheduler(cfg, caps)
    scheduler.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())