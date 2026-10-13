"""Render-pass processors: forward, deferred, post."""
from vulkan_renderer_sample.processors.forward import ForwardPass
from vulkan_renderer_sample.processors.deferred import DeferredPass
from vulkan_renderer_sample.processors.post import PostPass

__all__ = ["ForwardPass", "DeferredPass", "PostPass"]