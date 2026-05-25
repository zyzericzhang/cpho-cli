from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

from cpho_cli.core.index.ocr_cache import (
    OcrEngineDelta,
    OcrUpgradeDecisionRequired,
    detect_ocr_engine_upgrade,
)
from cpho_cli.core.index.hashing import TAG_SCHEMA_VERSION
from cpho_cli.core.index.storage import write_index
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
)


def _make_entry(
    problem_id: str,
    *,
    ocr_engine: str = "rapidocr",
    ocr_engine_version: str = "3.0",
    ocr_config_hash: str = "abc",
) -> IndexEntry:
    return IndexEntry(
        problem_id=problem_id,
        problem_path=Path(f"{problem_id}.pdf"),
        problem_page_range=(1, 1),
        answer_path=None,
        indexed_at=datetime.now(timezone.utc),
        fingerprint=IndexFingerprint(
            file=FileFingerprint(
                problem_sha256="a" * 64,
                answer_sha256=None,
                problem_size_bytes=1,
                answer_size_bytes=None,
                problem_mtime_ns=0,
            ),
            semantic=SemanticFingerprint(
                file_fp_hash="a" * 16,
                ocr_engine=ocr_engine,
                ocr_engine_version=ocr_engine_version,
                ocr_config_hash=ocr_config_hash,
                tag_prompt_version="v1",
                split_prompt_version="v1",
                tag_schema_version=TAG_SCHEMA_VERSION,
                model_name="m",
                model_temperature=0.0,
                vocabulary_version="builtin-v0.1",
            ),
        ),
        ocr_text_length=0,
        tag_prompt_version="v1",
    )


def test_detect_returns_none_when_no_index(tmp_path: Path) -> None:
    assert detect_ocr_engine_upgrade(tmp_path, "rapidocr", "3.0", "abc") is None


def test_detect_returns_none_when_engine_matches(tmp_path: Path) -> None:
    write_index(
        tmp_path / ".cpho" / "index.jsonl",
        [_make_entry("p1"), _make_entry("p2")],
    )

    assert detect_ocr_engine_upgrade(tmp_path, "rapidocr", "3.0", "abc") is None


def test_detect_returns_delta_on_version_bump(tmp_path: Path) -> None:
    write_index(
        tmp_path / ".cpho" / "index.jsonl",
        [_make_entry("p1"), _make_entry("p2")],
    )

    delta = detect_ocr_engine_upgrade(tmp_path, "rapidocr", "4.1", "abc")

    assert isinstance(delta, OcrEngineDelta)
    assert delta.old_version == "3.0"
    assert delta.new_version == "4.1"
    assert delta.affected_count == 2
    assert delta.affected_problem_ids == ["p1", "p2"]


def test_detect_returns_delta_on_config_hash_change(tmp_path: Path) -> None:
    write_index(tmp_path / ".cpho" / "index.jsonl", [_make_entry("p1")])

    delta = detect_ocr_engine_upgrade(tmp_path, "rapidocr", "3.0", "def")

    assert delta is not None
    assert delta.old_config_hash == "abc"
    assert delta.new_config_hash == "def"
    assert delta.affected_count == 1


def test_detect_returns_delta_on_engine_swap(tmp_path: Path) -> None:
    write_index(tmp_path / ".cpho" / "index.jsonl", [_make_entry("p1")])

    delta = detect_ocr_engine_upgrade(tmp_path, "paddleocr", "3.0", "abc")

    assert delta is not None
    assert delta.old_engine == "rapidocr"
    assert delta.new_engine == "paddleocr"


def test_detect_only_reports_affected(tmp_path: Path) -> None:
    write_index(
        tmp_path / ".cpho" / "index.jsonl",
        [
            _make_entry("stale", ocr_engine_version="3.0"),
            _make_entry("fresh", ocr_engine_version="4.1"),
        ],
    )

    delta = detect_ocr_engine_upgrade(tmp_path, "rapidocr", "4.1", "abc")

    assert delta is not None
    assert delta.affected_count == 1
    assert delta.affected_problem_ids == ["stale"]


def test_ocr_upgrade_decision_required_carries_delta() -> None:
    delta = OcrEngineDelta(
        old_engine="rapidocr",
        old_version="3.0",
        old_config_hash="abc",
        new_engine="rapidocr",
        new_version="4.1",
        new_config_hash="abc",
        affected_count=2,
        affected_problem_ids=["p1", "p2"],
    )

    exc = OcrUpgradeDecisionRequired(delta)

    assert exc.delta is delta
    assert str(exc).startswith("OCR 引擎升级:")


def test_ocr_engine_delta_summary_chinese() -> None:
    delta = OcrEngineDelta(
        old_engine="rapidocr",
        old_version="3.0",
        old_config_hash="abc",
        new_engine="rapidocr",
        new_version="4.1",
        new_config_hash="abc",
        affected_count=2,
        affected_problem_ids=["p1", "p2"],
    )

    assert delta.summary() == "OCR 引擎升级: rapidocr 3.0 → rapidocr 4.1; 受影响条目 2"


def test_detect_returns_none_for_stale_pre_021_rows(tmp_path: Path) -> None:
    path = tmp_path / ".cpho" / "index.jsonl"
    row = _make_entry("old").model_dump(mode="json")
    row.pop("problem_page_range")
    row["fingerprint"]["semantic"].pop("split_prompt_version")
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    assert detect_ocr_engine_upgrade(tmp_path, "rapidocr", "3.0", "abc") is None
