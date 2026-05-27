from __future__ import annotations

from pathlib import Path

from cpho_cli.core.documents import IMAGE_EXTENSIONS
from cpho_cli.models.config import StrictModel
from cpho_cli.models.llm import ModelCapabilities


class InputRoute(StrictModel):
    input_modality_used: str
    file_paths: list[Path]
    warning: str | None = None


def choose_input_route(file_paths: list[Path], capabilities: ModelCapabilities) -> InputRoute:
    pdfs = [path for path in file_paths if path.suffix.lower() == ".pdf"]
    images = [path for path in file_paths if path.suffix.lower() in IMAGE_EXTENSIONS]
    if pdfs and capabilities.supports_file:
        return InputRoute(input_modality_used="multimodal_pdf", file_paths=pdfs)
    if images and capabilities.supports_image:
        return InputRoute(input_modality_used="multimodal_image", file_paths=images)
    if file_paths:
        names = ", ".join(path.name for path in file_paths)
        return InputRoute(
            input_modality_used="ocr_text",
            file_paths=[],
            warning=f"模型不支持这些原始输入，已降级为 OCR 文本: {names}",
        )
    return InputRoute(input_modality_used="ocr_text", file_paths=[])
