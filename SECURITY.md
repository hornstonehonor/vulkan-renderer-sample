# Security Policy

## Scope

`vulkan-renderer-sample` is a **Vulkan renderer sample**. It links against a
system Vulkan loader and, optionally, vendor ICDs. It does **not** open sockets,
spawn subprocesses beyond the configured shader compiler, or touch files outside
`logs/`, `captures/`, and `shader_cache/`.

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | ✅        |
| 0.5.x   | ⚠️ security only |
| < 0.5   | ❌        |

## Reporting a vulnerability

Please email `security@<org>.example` with:

- A minimal reproducer (ideally a `--backend=mock` frame trace).
- The exact commit SHA.
- Affected driver + loader versions.

We aim to triage within **5 business days**.

## Known sharp edges

- The `services/shader_compiler` bridges to `glslangValidator` / `dxc` if
  present on `PATH`. Pin the compiler version in CI; mismatched SPIR-V can trip
  validation layers.
- `drivers/capture` writes raw frames to disk. Do not enable on untrusted
  paths.
- Validation layers are **on by default** in debug builds. Disabling them in a
  released build is a bug, not a feature.