from __future__ import annotations

from pathlib import Path


def test_phase05_docs_open_source_acceptance() -> None:
    required = [
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        ".github/assets/cpho-demo.svg",
        ".github/ISSUE_TEMPLATE/bug_report.md",
        ".github/ISSUE_TEMPLATE/feature_request.md",
        "docs/user/README.md",
        "docs/user/extensions.md",
        "examples/README.md",
    ]
    for path in required:
        assert Path(path).is_file(), path

    readme = Path("README.md").read_text(encoding="utf-8")
    user_index = Path("docs/user/README.md").read_text(encoding="utf-8")
    extensions = Path("docs/user/extensions.md").read_text(encoding="utf-8")

    assert "Quick Start" in readme
    assert "Out of Scope" in readme
    assert "/explain" in readme
    assert "compose build" in readme
    assert "solve.md" in user_index
    assert "compose.md" in user_index
    assert "YAML 配置式 skill" in extensions
    assert "pip 安装第三方 skill" in extensions
