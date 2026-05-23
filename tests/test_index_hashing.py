from __future__ import annotations

from pathlib import Path

from cpho_cli.core.index.hashing import sha256_file, sha256_json


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
