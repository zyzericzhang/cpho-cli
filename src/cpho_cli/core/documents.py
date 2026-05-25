from __future__ import annotations

from pathlib import Path

from cpho_cli.models.documents import DocumentInput, DocumentPage

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff"}


def load_document(path: Path) -> DocumentInput:
    if path.suffix.lower() in IMAGE_EXTENSIONS:
        return DocumentInput(
            path=path,
            pages=[DocumentPage(page_number=1, image_bytes=path.read_bytes())],
        )

    if path.suffix.lower() == ".pdf":
        try:
            import fitz
        except ImportError as exc:  # pragma: no cover - dependency managed by pyproject
            raise RuntimeError("PyMuPDF is required to read PDF files.") from exc
        pages: list[DocumentPage] = []
        with fitz.open(path) as document:
            for index, page in enumerate(document, start=1):
                pixmap = page.get_pixmap()
                pages.append(
                    DocumentPage(
                        page_number=index,
                        embedded_text=page.get_text() or "",
                        image_bytes=pixmap.tobytes("png"),
                    )
                )
        return DocumentInput(path=path, pages=pages)

    raise ValueError(f"Unsupported document type: {path.suffix}")
