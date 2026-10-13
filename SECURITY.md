# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | security fixes only |
| < 0.3   | no        |

## Threat model

`ai-texture-material-generator` is a local desktop tool. It:

- Reads images from user-chosen paths.
- Writes texture outputs to a user-chosen output directory.
- Downloads model weights from configured mirrors on first run.

It does **not** open inbound sockets, phone home, or execute model files
as code. Model weights are loaded through `safetensors` / `onnxruntime`
only — never `torch.load` with `weights_only=False`.

## Reporting a vulnerability

Open a private security advisory on GitHub, or email
`security@ai-texture-material-generator.local`. Include a minimal
reproducer and the affected version. We aim to acknowledge within 72h.

## Out of scope

- Prompts producing "offensive" imagery — that's a moderation concern,
  not a memory-safety one.
- Third-party model weights from unofficial mirrors.
- Denial of service via absurd output resolutions on your own machine.