# Setup decisions

- Engine: `headpiece747/ninfer-5090-windows` v1.1.0 prebuilt release.
- Model: `satellitedown/Huihui-Qwen3.8-27B-abliterated-NVFP4-NInfer-v3`.
- Profile: Vision + MTP5 + NVFP4 KV, one active request, 262,144-token ceiling.
- Network: localhost only (`127.0.0.1:39217`), CORS disabled.
- Integrity: fixed engine release SHA-256 plus Hugging Face LFS model SHA-256 when exposed.
- Download routing: `hf-mirror.com` first, then official Hugging Face; selectable in setup.ps1.
