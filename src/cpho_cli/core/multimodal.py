from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from cpho_cli.models.llm import ModelCapabilities

_IMAGE_MIME_BY_SUFFIX = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def _data_url(path: Path, mime_type: str) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def build_multimodal_content(
    text: str,
    file_paths: list[Path],
    capabilities: ModelCapabilities,
) -> list[dict[str, Any]] | None:
    blocks: list[dict[str, Any]] = [{"type": "text", "text": text}]
    for path in file_paths:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            if not capabilities.supports_file:
                return None
            blocks.append(
                {
                    "type": "file",
                    "file": {
                        "filename": path.name,
                        "file_data": _data_url(path, "application/pdf"),
                    },
                }
            )
            continue

        mime_type = _IMAGE_MIME_BY_SUFFIX.get(suffix)
        if mime_type is None or not capabilities.supports_image:
            return None
        blocks.append({"type": "image_url", "image_url": {"url": _data_url(path, mime_type)}})

    return blocks
