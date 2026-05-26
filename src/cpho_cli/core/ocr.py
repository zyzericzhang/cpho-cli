from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

from cpho_cli.models.documents import DocumentInput
from cpho_cli.models.ocr import OCRBlock, OCRPageResult, OCRResult


class OCRProvider(Protocol):
    def extract(self, document: DocumentInput) -> OCRResult:
        """Extract OCR text from a document."""


def normalize_ocr_blocks(
    page_number: int,
    raw_blocks: Sequence[dict[str, Any]],
    low_confidence_threshold: float = 0.6,
) -> list[OCRBlock]:
    blocks: list[OCRBlock] = []
    for raw in raw_blocks:
        confidence = raw.get("confidence")
        blocks.append(
            OCRBlock(
                text=str(raw.get("text", "")),
                page_number=page_number,
                confidence=confidence,
                bbox=raw.get("bbox"),
                low_confidence=confidence is not None and confidence < low_confidence_threshold,
            )
        )
    return blocks


class RapidOCRProvider:
    def __init__(self, low_confidence_threshold: float = 0.6) -> None:
        self.low_confidence_threshold = low_confidence_threshold

    def extract(self, document: DocumentInput) -> OCRResult:
        try:
            from rapidocr import RapidOCR
        except ImportError as exc:  # pragma: no cover - dependency managed by pyproject
            raise RuntimeError("rapidocr is required for OCR extraction.") from exc

        engine = RapidOCR()
        pages: list[OCRPageResult] = []
        for page in document.pages:
            raw_blocks: list[dict[str, Any]] = []
            if page.embedded_text.strip():
                raw_blocks.append(
                    {"text": page.embedded_text, "confidence": 1.0, "bbox": None}
                )
            elif page.image_bytes is not None:
                result = engine(page.image_bytes)
                for item in getattr(result, "txts", []) or []:
                    raw_blocks.append({"text": item, "confidence": None, "bbox": None})
            pages.append(
                OCRPageResult(
                    page_number=page.page_number,
                    blocks=normalize_ocr_blocks(
                        page.page_number, raw_blocks, self.low_confidence_threshold
                    ),
                )
            )
        return OCRResult(pages=pages)

