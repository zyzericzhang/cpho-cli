from __future__ import annotations

from pathlib import Path


def test_readme_describes_current_quickstart_and_scope() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    for phrase in [
        "Quick Start",
        "/explain",
        "/probe",
        "/search-related",
        "compose build",
        "Out of Scope",
        ".github/assets/cpho-demo.svg",
    ]:
        assert phrase in text
    assert "cpho eval" not in text


def test_open_source_metadata_files_exist() -> None:
    for path in [
        "LICENSE",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        ".github/ISSUE_TEMPLATE/bug_report.md",
        ".github/ISSUE_TEMPLATE/feature_request.md",
        ".github/assets/cpho-demo.svg",
    ]:
        assert Path(path).is_file(), path


def test_gitignore_excludes_claude_directory() -> None:
    text = Path(".gitignore").read_text(encoding="utf-8")
    assert ".claude/" in text
