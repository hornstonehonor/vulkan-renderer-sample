"""Shader compile service.

Bridges to an external compiler if present on PATH:
  glslangValidator  (GLSL -> SPIR-V)
  dxc               (HLSL -> SPIR-V)
  glslc             (shaderc)

Cache key: sha256(source) + compiler id + compiler version. Cache lives
in `shader_cache/`. Mismatched compiler versions do *not* reuse a blob —
that is the one thing that reliably produces validation-layer noise.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from vulkan_renderer_sample.utils.logging import get_logger

log = get_logger("shader")

_COMPILERS = {
    ".vert": ("glslangValidator", ["-V", "--target-env", "vulkan1.3"]),
    ".frag": ("glslangValidator", ["-V", "--target-env", "vulkan1.3"]),
    ".comp": ("glslc", ["-fshader-stage=compute", "--target-env=vulkan1.3"]),
    ".hlsl": ("dxc", ["-spirv", "-T", "vs_6_6", "-E", "main"]),
}


@dataclass(slots=True, frozen=True)
class CompileResult:
    source: Path
    spirv: Path
    cached: bool
    compiler: str


class ShaderCompiler:
    def __init__(self, cache_dir: Path, force: bool = False) -> None:
        self._cache = cache_dir
        self._cache.mkdir(parents=True, exist_ok=True)
        self._force = force

    def _key(self, source: Path) -> str:
        digest = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
        compiler, _ = _COMPILERS.get(source.suffix, ("glslangValidator", []))
        version = self._compiler_version(compiler)
        return f"{digest}_{compiler}_{version}"

    def _compiler_version(self, compiler: str) -> str:
        exe = shutil.which(compiler)
        if exe is None:
            return "none"
        try:
            out = subprocess.run([exe, "--version"], capture_output=True,
                                 text=True, timeout=5, check=False)
            return (out.stdout or out.stderr).splitlines()[0][:32] if (out.stdout or out.stderr) else "unknown"
        except (OSError, subprocess.SubprocessError):
            return "unknown"

    def compile(self, source: Path) -> CompileResult:
        key = self._key(source)
        out = self._cache / f"{source.stem}_{key}.spv"
        if out.exists() and not self._force:
            return CompileResult(source, out, cached=True, compiler="cache")
        compiler, flags = _COMPILERS.get(source.suffix, ("glslangValidator", []))
        exe = shutil.which(compiler)
        if exe is None:
            raise FileNotFoundError(
                f"no shader compiler for {source.suffix}; install {compiler}"
            )
        subprocess.run([exe, *flags, "-o", str(out), str(source)],
                       check=True, capture_output=True)
        log.info("shader_compiled", source=str(source), spirv=str(out))
        return CompileResult(source, out, cached=False, compiler=compiler)