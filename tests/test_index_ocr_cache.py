from __future__ import annotations

import re
from pathlib import Path

from cpho_cli.core.index.hashing import sha256_file
from cpho_cli.core.index.ocr_cache import CachedOCRProvider, RAPIDOCR_ENGINE_NAME
from cpho_cli.models.documents import DocumentInput, DocumentPage
from cpho_cli.models.ocr import OCRBlock, OCRPageResult, OCRResult


class FakeOCRProvider:
    def __init__(self, text: str = "cached text") -> None:
        self.text = text
        self.calls = 0

    def extract(self, document: DocumentInput) -> OCRResult:
        self.calls += 1
        return OCRResult(
            pages=[
                OCRPageResult(
                    page_number=1,
                    blocks=[
                        OCRBlock(
                            text=self.text,
                            page_number=1,
                            confidence=1.0,
                        )
                    ],
                )
            ]
        )


def _document(path: Path) -> DocumentInput:
    return DocumentInput(path=path, pages=[DocumentPage(page_number=1)])


def test_cache_miss_calls_inner_and_writes(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem bytes")
    cache_dir = tmp_path / "cache"
    inner = FakeOCRProvider("first result")
    provider = CachedOCRProvider(inner, cache_dir, RAPIDOCR_ENGINE_NAME, "3.0")

    result = provider.extract(_document(problem))

    expected_key = f"{sha256_file(problem)[:16]}__rapidocr_3.0.json"
    assert result.text == "first result"
    assert inner.calls == 1
    assert provider.last_was_cached is False
    assert (cache_dir / expected_key).exists()


def test_cache_hit_skips_inner(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem bytes")
    inner = FakeOCRProvider("first result")
    provider = CachedOCRProvider(inner, tmp_path / "cache", RAPIDOCR_ENGINE_NAME, "3.0")

    first = provider.extract(_document(problem))
    second = provider.extract(_document(problem))

    assert inner.calls == 1
    assert provider.last_was_cached is True
    assert second == first


def test_cache_key_format(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem bytes")
    provider = CachedOCRProvider(
        FakeOCRProvider(), tmp_path / "cache", RAPIDOCR_ENGINE_NAME, "3.0"
    )

    provider.extract(_document(problem))

    names = [path.name for path in (tmp_path / "cache").iterdir()]
    assert len(names) == 1
    assert re.match(r"^[0-9a-f]{16}__rapidocr_3\.0\.json$", names[0])


def test_different_file_content_different_key(tmp_path: Path) -> None:
    first_path = tmp_path / "first.pdf"
    second_path = tmp_path / "second.pdf"
    first_path.write_bytes(b"first")
    second_path.write_bytes(b"second")
    provider = CachedOCRProvider(FakeOCRProvider(), tmp_path / "cache", "rapidocr", "3.0")

    first = provider.extract(_document(first_path))
    second = provider.extract(_document(second_path))

    cache_files = sorted((tmp_path / "cache").glob("*.json"))
    assert len(cache_files) == 2
    assert cache_files[0].name != cache_files[1].name
    assert OCRResult.model_validate_json(cache_files[0].read_text(encoding="utf-8")) in [
        first,
        second,
    ]
    assert OCRResult.model_validate_json(cache_files[1].read_text(encoding="utf-8")) in [
        first,
        second,
    ]


def test_different_engine_version_different_key(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem bytes")
    cache_dir = tmp_path / "cache"

    CachedOCRProvider(FakeOCRProvider("v3"), cache_dir, "rapidocr", "3.0").extract(
        _document(problem)
    )
    CachedOCRProvider(FakeOCRProvider("v4"), cache_dir, "rapidocr", "4.0").extract(
        _document(problem)
    )

    names = {path.name for path in cache_dir.glob("*.json")}
    assert len(names) == 2
    assert any(name.endswith("__rapidocr_3.0.json") for name in names)
    assert any(name.endswith("__rapidocr_4.0.json") for name in names)


def test_cache_roundtrip_preserves_chinese(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem bytes")
    provider = CachedOCRProvider(
        FakeOCRProvider("牛顿第二定律"), tmp_path / "cache", "rapidocr", "3.0"
    )

    provider.extract(_document(problem))
    cached = provider.extract(_document(problem))

    assert provider.last_was_cached is True
    assert cached.text == "牛顿第二定律"


def test_cache_dir_created_lazily(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem bytes")
    cache_dir = tmp_path / "deeply" / "nested" / "ocr"
    provider = CachedOCRProvider(FakeOCRProvider(), cache_dir, "rapidocr", "3.0")

    assert not cache_dir.exists()
    provider.extract(_document(problem))

    assert cache_dir.exists()
