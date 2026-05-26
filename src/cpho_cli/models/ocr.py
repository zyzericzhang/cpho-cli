from __future__ import annotations

from pydantic import BaseModel


class OCRBlock(BaseModel):
    text: str
    page_number: int
    confidence: float | None = None
    bbox: list[float] | None = None
    low_confidence: bool = False


class OCRPageResult(BaseModel):
    page_number: int
    blocks: list[OCRBlock]


class OCRResult(BaseModel):
    pages: list[OCRPageResult]

    @property
    def text(self) -> str:
        return "\n".join(block.text for page in self.pages for block in page.blocks)

