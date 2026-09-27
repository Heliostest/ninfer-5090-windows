from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Optional

from huggingface_hub import HfApi, snapshot_download


REPO_ID = "satellitedown/Huihui-Qwen3.8-27B-abliterated-NVFP4-NInfer-v3"
ALLOW_PATTERNS = [
    "*.ninfer",
    "SHA256SUMS",
    "*.json",
    "README*",
    "LICENSE*",
    "NOTICE*",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    total = path.stat().st_size
    done = 0
    with path.open("rb") as handle:
        while chunk := handle.read(64 * 1024 * 1024):
            digest.update(chunk)
            done += len(chunk)
            print(
                f"\rVerifying model: {done / total * 100:5.1f}% "
                f"({done / 1024**3:.2f}/{total / 1024**3:.2f} GiB)",
                end="",
                flush=True,
            )
    print()
    return digest.hexdigest()


def expected_lfs_hash(filename: str, endpoint: str) -> Optional[str]:
    info = HfApi(endpoint=endpoint).model_info(REPO_ID, files_metadata=True)
    for sibling in info.siblings or []:
        if sibling.rfilename != filename:
            continue
        lfs = getattr(sibling, "lfs", None)
        value = getattr(lfs, "sha256", None) if lfs is not None else None
        if value:
            return str(value).lower()
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument(
        "--source",
        choices=("Auto", "HfMirror", "HuggingFace"),
        default="Auto",
        help="Auto tries hf-mirror.com first, then the official Hugging Face endpoint.",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    model_dir = root / "models" / "satellitedown_huihui_qwen3_8_27b_ninfer_v3"
    model_dir.mkdir(parents=True, exist_ok=True)

    endpoints = {
        "Auto": ("https://hf-mirror.com", "https://huggingface.co"),
        "HfMirror": ("https://hf-mirror.com",),
        "HuggingFace": ("https://huggingface.co",),
    }[args.source]

    selected_endpoint: Optional[str] = None
    failures: list[str] = []
    for endpoint in endpoints:
        print(f"Downloading {REPO_ID} from {endpoint} into {model_dir}")
        try:
            snapshot_download(
                repo_id=REPO_ID,
                local_dir=model_dir,
                allow_patterns=ALLOW_PATTERNS,
                endpoint=endpoint,
            )
            selected_endpoint = endpoint
            break
        except Exception as error:  # noqa: BLE001 - each endpoint gets a fallback attempt
            failures.append(f"{endpoint}: {error}")
            print(f"Endpoint failed: {error}")

    if selected_endpoint is None:
        details = "\n".join(failures)
        raise SystemExit(f"All configured download endpoints failed:\n{details}")

    artifacts = sorted(model_dir.rglob("*.ninfer"), key=lambda item: item.stat().st_size, reverse=True)
    if not artifacts:
        raise SystemExit("Download completed, but the repository contained no .ninfer artifact.")
    if len(artifacts) > 1:
        print(f"Found {len(artifacts)} artifacts; selecting the largest one.")

    artifact = artifacts[0].resolve()
    expected = expected_lfs_hash(artifact.name, selected_endpoint)
    actual = sha256_file(artifact)
    if expected and actual != expected:
        raise SystemExit(f"Model SHA-256 mismatch: expected {expected}, got {actual}")

    (root / "MODEL_PATH.txt").write_text(str(artifact), encoding="utf-8")
    (root / "MODEL_SHA256.txt").write_text(f"{actual}  {artifact.name}\n", encoding="ascii")

    print(f"Model:  {artifact}")
    print(f"Source: {selected_endpoint}")
    print(f"Size:   {artifact.stat().st_size / 1024**3:.2f} GiB")
    print(f"SHA256: {actual}")
    if expected:
        print("Hugging Face LFS SHA-256 verified.")
    else:
        print("WARNING: no LFS SHA-256 metadata was exposed; the computed hash was recorded locally.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
