from pathlib import Path

from cpho_cli.core.workspace import discover_workspace
from cpho_cli.models.documents import PaperAnswerPair, PaperFile


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


def test_discovers_chinese_paper_answer_pairs(tmp_path: Path) -> None:
    touch(tmp_path / "力学2试题.pdf")
    touch(tmp_path / "力学2解析.pdf")
    touch(tmp_path / "理论5试题.pdf")
    touch(tmp_path / "理论5-答案.pdf")

    result = discover_workspace(tmp_path)

    assert {pair.paper.path.name for pair in result.pairs} == {"力学2试题.pdf", "理论5试题.pdf"}
    assert {pair.answer.path.name for pair in result.pairs if pair.answer is not None} == {
        "力学2解析.pdf",
        "理论5-答案.pdf",
    }
    assert all(isinstance(pair, PaperAnswerPair) for pair in result.pairs)
    assert all(pair.paper.total_pages == 1 for pair in result.pairs)


def test_discovers_standalone_images_as_single_page_papers(tmp_path: Path) -> None:
    touch(tmp_path / "scan-a.png")
    touch(tmp_path / "scan-b.jpg")
    touch(tmp_path / "scan-c.gif")

    result = discover_workspace(tmp_path)

    assert result.pairs == []
    assert {paper.path.name for paper in result.unmatched_problems} == {
        "scan-a.png",
        "scan-b.jpg",
        "scan-c.gif",
    }
    assert all(isinstance(paper, PaperFile) for paper in result.unmatched_problems)
    assert all(paper.total_pages == 1 for paper in result.unmatched_problems)
