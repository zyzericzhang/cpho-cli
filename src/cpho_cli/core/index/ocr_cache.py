from __future__ import annotations

from pathlib import Path

from cpho_cli.core.index.hashing import sha256_file, sha256_json
from cpho_cli.core.ocr import OCRProvider
from cpho_cli.models.documents import DocumentInput
from cpho_cli.models.ocr import OCRResult

OCR_CACHE_DIRNAME = ".cpho/cache/ocr"
RAPIDOCR_ENGINE_NAME = "rapidocr"


def _rapidocr_version() -> str:
    try:
        import rapidocr

        return getattr(rapidocr, "__version__", "unknown")
    except ImportError:
        return "unknown"


def ocr_config_hash(ocr_config: dict[str, object]) -> str:
    return sha256_json(ocr_config)


class CachedOCRProvider:
    """File-content-addressed OCR cache wrapper.

    Key = sha256(file_bytes)[:16] + engine_name + engine_version, so engine upgrades
    naturally invalidate without deleting old entries. last_was_cached attribute reports
    the most recent extract() decision for stats aggregation.
    """

    def __init__(
        self,
        inner: OCRProvider,
        cache_dir: Path,
        engine_name: str,
        engine_version: str,
    ) -> None:
        self.inner = inner
        self.cache_dir = cache_dir
        self.engine_name = engine_name
        self.engine_version = engine_version
        self.last_was_cached = False

    def extract(self, document: DocumentInput) -> OCRResult:
        file_hash = sha256_file(document.path)
        key = f"{file_hash[:16]}__{self.engine_name}_{self.engine_version}.json"
        path = self.cache_dir / key
        if path.exists():
            self.last_was_cached = True
            # Local cache is recoverable, not authoritative; force rebuild regenerates it.
            return OCRResult.model_validate_json(path.read_text(encoding="utf-8"))

        self.last_was_cached = False
        result = self.inner.extract(document)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        return result
