from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from cpho_cli.core.index.hashing import (
    compose_file_fingerprint,
    compose_semantic_fingerprint,
    compose_user_learning_fingerprint,
    sha256_file,
    sha256_json,
)
from cpho_cli.models.index import UserNotebookEntry, UserLearningFingerprint


def test_sha256_file_deterministic(tmp_path: Path) -> None:
    problem_a = tmp_path / "a.pdf"
    problem_b = tmp_path / "b.pdf"
    problem_a.write_bytes(b"same bytes")
    problem_b.write_bytes(b"same bytes")

    assert sha256_file(problem_a) == sha256_file(problem_b)


def test_sha256_file_changes_with_content(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_text("hello", encoding="utf-8")
    first_digest = sha256_file(problem)

    problem.write_text("world", encoding="utf-8")

    assert sha256_file(problem) != first_digest


def test_sha256_json_sort_independent() -> None:
    assert sha256_json({"a": 1, "b": 2}) == sha256_json({"b": 2, "a": 1})


def test_sha256_json_handles_chinese() -> None:
    assert sha256_json({"x": "牛顿"}) == sha256_json({"x": "牛顿"})
    assert sha256_json({"x": "牛顿"}) != sha256_json({"x": "newton"})


def test_sha256_json_handles_path() -> None:
    sha256_json({"p": Path("a/b.pdf")})


def test_compose_file_fingerprint_with_answer(tmp_path: Path) -> None:
    problem_bytes = b"problem"
    answer_bytes = b"answer"
    problem = tmp_path / "problem.pdf"
    answer = tmp_path / "answer.pdf"
    problem.write_bytes(problem_bytes)
    answer.write_bytes(answer_bytes)

    fingerprint = compose_file_fingerprint(problem, answer)

    assert fingerprint.problem_sha256 == hashlib.sha256(problem_bytes).hexdigest()
    assert fingerprint.answer_sha256 == hashlib.sha256(answer_bytes).hexdigest()
    assert fingerprint.problem_size_bytes == len(problem_bytes)
    assert fingerprint.answer_size_bytes == len(answer_bytes)


def test_compose_file_fingerprint_no_answer(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem")

    fingerprint = compose_file_fingerprint(problem, None)

    assert fingerprint.answer_sha256 is None
    assert fingerprint.answer_size_bytes is None


def test_semantic_fingerprint_diff_on_engine_version(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem")
    file_fp = compose_file_fingerprint(problem, None)

    first = compose_semantic_fingerprint(
        file_fp,
        ocr_engine="rapidocr",
        ocr_engine_version="3.0",
        ocr_config={},
        tag_prompt_version="v1",
        tag_schema_version="v1",
        model_name="model",
        model_temperature=0.0,
        vocabulary_version="builtin-v0.1",
    )
    second = compose_semantic_fingerprint(
        file_fp,
        ocr_engine="rapidocr",
        ocr_engine_version="4.0",
        ocr_config={},
        tag_prompt_version="v1",
        tag_schema_version="v1",
        model_name="model",
        model_temperature=0.0,
        vocabulary_version="builtin-v0.1",
    )

    assert first != second
    assert first.ocr_engine_version != second.ocr_engine_version


def test_semantic_fingerprint_diff_on_vocab_version(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem")
    file_fp = compose_file_fingerprint(problem, None)

    first = compose_semantic_fingerprint(
        file_fp,
        "rapidocr",
        "3.0",
        {},
        "v1",
        "v1",
        "model",
        0.0,
        "builtin-v0.1+ws-none+pv-none",
    )
    second = compose_semantic_fingerprint(
        file_fp,
        "rapidocr",
        "3.0",
        {},
        "v1",
        "v1",
        "model",
        0.0,
        "builtin-v0.1+ws-abcd1234+pv-none",
    )

    assert first != second


def test_semantic_fingerprint_diff_on_prompt_version(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem")
    file_fp = compose_file_fingerprint(problem, None)

    first = compose_semantic_fingerprint(file_fp, "rapidocr", "3.0", {}, "v1", "v1", "model", 0.0, "vocab")
    second = compose_semantic_fingerprint(file_fp, "rapidocr", "3.0", {}, "v2", "v1", "model", 0.0, "vocab")

    assert first != second


def test_semantic_fingerprint_diff_on_temperature(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem")
    file_fp = compose_file_fingerprint(problem, None)

    first = compose_semantic_fingerprint(file_fp, "rapidocr", "3.0", {}, "v1", "v1", "model", 0.0, "vocab")
    second = compose_semantic_fingerprint(file_fp, "rapidocr", "3.0", {}, "v1", "v1", "model", 0.2, "vocab")

    assert first != second


def test_semantic_fingerprint_diff_on_ocr_config(tmp_path: Path) -> None:
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"problem")
    file_fp = compose_file_fingerprint(problem, None)

    first = compose_semantic_fingerprint(
        file_fp,
        "rapidocr",
        "3.0",
        {"low_confidence_threshold": 0.6},
        "v1",
        "v1",
        "model",
        0.0,
        "vocab",
    )
    second = compose_semantic_fingerprint(
        file_fp,
        "rapidocr",
        "3.0",
        {"low_confidence_threshold": 0.7},
        "v1",
        "v1",
        "model",
        0.0,
        "vocab",
    )

    assert first.ocr_config_hash != second.ocr_config_hash


def test_user_learning_fp_none_when_no_notebook() -> None:
    assert compose_user_learning_fingerprint(None) == UserLearningFingerprint()


def test_user_learning_fp_changes_on_notes_edit() -> None:
    first = UserNotebookEntry(problem_id="p1", key_points=["Newton"])
    second = UserNotebookEntry(problem_id="p1", key_points=["Energy"])

    assert compose_user_learning_fingerprint(first).notes_sha256 != compose_user_learning_fingerprint(second).notes_sha256


def test_user_learning_fp_qa_history_phase2_none() -> None:
    notebook = UserNotebookEntry(problem_id="p1", key_points=["Newton"], user_tags=["mechanics"])

    assert compose_user_learning_fingerprint(notebook).qa_history_sha256 is None


def test_user_learning_fp_ignores_updated_at() -> None:
    first = UserNotebookEntry(problem_id="p1", key_points=["Newton"], updated_at=datetime(2024, 1, 1))
    second = UserNotebookEntry(problem_id="p1", key_points=["Newton"], updated_at=datetime(2025, 1, 1))

    assert compose_user_learning_fingerprint(first) == compose_user_learning_fingerprint(second)
