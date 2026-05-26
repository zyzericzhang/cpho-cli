import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from cpho_cli.core.index import IndexNotFoundError
from cpho_cli.core.index.storage import load_existing_index_for_rebuild, load_index, write_index
from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
)


def _entry(problem_id: str = "p1", **overrides: object) -> IndexEntry:
    data = {
        "problem_id": problem_id,
        "problem_path": Path(f"{problem_id}.pdf"),
        "problem_page_range": (1, 1),
        "answer_path": None,
        "indexed_at": datetime.now(timezone.utc),
        "fingerprint": IndexFingerprint(
            file=FileFingerprint(
                problem_sha256="a" * 64,
                answer_sha256=None,
                problem_size_bytes=1,
                answer_size_bytes=None,
                problem_mtime_ns=0,
            ),
            semantic=SemanticFingerprint(
                file_fp_hash="x",
                ocr_engine="rapidocr",
                ocr_engine_version="3.0",
                ocr_config_hash="y",
                tag_prompt_version="v1",
                split_prompt_version="v1",
                tag_schema_version="v2",
                model_name="m",
                model_temperature=0.0,
                vocabulary_version="builtin-v0.1+ws-none+pv-none",
            ),
        ),
        "ocr_text_length": 0,
        "tag_prompt_version": "v1",
    }
    data.update(overrides)
    return IndexEntry(**data)


def test_write_index_creates_jsonl(tmp_path: Path) -> None:
    path = tmp_path / ".cpho" / "index.jsonl"
    entries = [_entry("p1"), _entry("p2")]

    write_index(path, entries)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert [IndexEntry.model_validate_json(line) for line in lines] == entries


def test_write_index_uses_atomic_rename(tmp_path: Path) -> None:
    path = tmp_path / ".cpho" / "index.jsonl"

    write_index(path, [_entry()])

    assert path.exists()
    assert not (tmp_path / ".cpho" / "index.jsonl.tmp").exists()


def test_write_index_overwrites_existing(tmp_path: Path) -> None:
    path = tmp_path / ".cpho" / "index.jsonl"

    write_index(path, [_entry("p1"), _entry("p2"), _entry("p3")])
    write_index(path, [_entry("p4")])

    assert [entry.problem_id for entry in load_index(tmp_path)] == ["p4"]


def test_load_index_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(IndexNotFoundError):
        load_index(tmp_path)


def test_load_index_skips_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / ".cpho" / "index.jsonl"
    path.parent.mkdir(parents=True)
    entry = _entry()
    path.write_text(
        entry.model_dump_json() + "\n\n" + entry.model_dump_json() + "\n",
        encoding="utf-8",
    )

    assert load_index(tmp_path) == [entry, entry]


def test_load_index_utf8_chinese(tmp_path: Path) -> None:
    path = tmp_path / ".cpho" / "index.jsonl"
    entry = _entry(difficulty_aspects=["选系统时容易忽略约束"])

    write_index(path, [entry])

    assert load_index(tmp_path)[0].difficulty_aspects == ["选系统时容易忽略约束"]


def test_load_existing_index_for_rebuild_discards_pre_021_rows(tmp_path: Path) -> None:
    path = tmp_path / ".cpho" / "index.jsonl"
    entry = _entry().model_dump(mode="json")
    entry.pop("problem_page_range")
    entry["fingerprint"]["semantic"].pop("split_prompt_version")
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(entry) + "\n", encoding="utf-8")

    with pytest.raises(Exception):
        load_index(tmp_path)

    result = load_existing_index_for_rebuild(tmp_path, expected_schema_version="v2")

    assert result.entries == []
    assert result.stale_reason is not None
    assert "stale" in result.stale_reason


def test_load_existing_index_for_rebuild_discards_legacy_report_path(
    tmp_path: Path,
) -> None:
    path = tmp_path / ".cpho" / "index.jsonl"
    entry = _entry().model_dump(mode="json")
    entry["solve_" + "report_path"] = "output/p1-report.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(entry) + "\n", encoding="utf-8")

    result = load_existing_index_for_rebuild(tmp_path, expected_schema_version="v3")

    assert result.entries == []
    assert result.stale_reason is not None
    assert "stale" in result.stale_reason


def test_load_existing_index_for_rebuild_discards_legacy_report_source(
    tmp_path: Path,
) -> None:
    path = tmp_path / ".cpho" / "index.jsonl"
    entry = _entry().model_dump(mode="json")
    entry["physics_model_tags"] = [
        {"internal_id": "newton_second_law", "source": "solve_report", "confidence": None}
    ]
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(entry) + "\n", encoding="utf-8")

    result = load_existing_index_for_rebuild(tmp_path, expected_schema_version="v3")

    assert result.entries == []
    assert result.stale_reason is not None
    assert "stale" in result.stale_reason
