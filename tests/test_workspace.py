from pathlib import Path

from cpho_cli.core.workspace import discover_workspace


def touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")


def test_discovers_problem_answer_pair(tmp_path: Path) -> None:
    touch(tmp_path / "2024-final-p1.pdf")
    touch(tmp_path / "2024-final-p1-answer.pdf")

    result = discover_workspace(tmp_path)

    assert len(result.pairs) == 1
    assert result.pairs[0].problem.path.name == "2024-final-p1.pdf"
    assert result.pairs[0].answer is not None
    assert result.pairs[0].answer.path.name == "2024-final-p1-answer.pdf"


def test_unmatched_problem_is_reported(tmp_path: Path) -> None:
    touch(tmp_path / "lonely.pdf")

    result = discover_workspace(tmp_path)

    assert result.pairs == []
    assert result.unmatched_problems[0].path.name == "lonely.pdf"


def test_ambiguous_answer_is_not_selected(tmp_path: Path) -> None:
    touch(tmp_path / "p1.pdf")
    touch(tmp_path / "p1-answer.pdf")
    touch(tmp_path / "answers/p1-solution.pdf")

    result = discover_workspace(tmp_path)

    assert result.pairs == []
    assert result.ambiguous[0].problem.path.name == "p1.pdf"
    assert len(result.ambiguous[0].candidates) == 2

