from __future__ import annotations

from collections import Counter
from pathlib import Path

from pydantic import Field

from cpho_cli.core.index import IndexBuildError
from cpho_cli.core.index.hashing import TAG_SCHEMA_VERSION, sha256_file, sha256_json
from cpho_cli.core.index.storage import load_existing_index_for_rebuild
from cpho_cli.core.ocr import OCRProvider
from cpho_cli.models.config import StrictModel
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


class OcrEngineDelta(StrictModel):
    old_engine: str
    old_version: str
    old_config_hash: str
    new_engine: str
    new_version: str
    new_config_hash: str
    affected_count: int
    affected_problem_ids: list[str] = Field(default_factory=list)

    def summary(self) -> str:
        return (
            f"OCR 引擎升级: {self.old_engine} {self.old_version} → "
            f"{self.new_engine} {self.new_version}; 受影响条目 {self.affected_count}"
        )


class OcrUpgradeDecisionRequired(IndexBuildError):
    def __init__(self, delta: OcrEngineDelta) -> None:
        self.delta = delta
        super().__init__(delta.summary())


def detect_ocr_engine_upgrade(
    workspace_root: Path,
    current_engine: str,
    current_version: str,
    current_config_hash: str,
) -> OcrEngineDelta | None:
    load_result = load_existing_index_for_rebuild(workspace_root, TAG_SCHEMA_VERSION)
    if load_result.stale_reason is not None:
        return None
    entries = load_result.entries

    if not entries:
        return None

    current = (current_engine, current_version, current_config_hash)
    affected: list[tuple[str, str, str, str]] = []
    for entry in entries:
        semantic = entry.fingerprint.semantic
        stored = (
            semantic.ocr_engine,
            semantic.ocr_engine_version,
            semantic.ocr_config_hash,
        )
        if stored != current:
            affected.append((entry.problem_id, *stored))

    if not affected:
        return None

    old_engine, old_version, old_config_hash = Counter(
        (engine, version, config_hash) for _, engine, version, config_hash in affected
    ).most_common(1)[0][0]
    return OcrEngineDelta(
        old_engine=old_engine,
        old_version=old_version,
        old_config_hash=old_config_hash,
        new_engine=current_engine,
        new_version=current_version,
        new_config_hash=current_config_hash,
        affected_count=len(affected),
        affected_problem_ids=[problem_id for problem_id, *_ in affected],
    )
