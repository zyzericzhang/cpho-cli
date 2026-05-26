from __future__ import annotations

from pathlib import Path


CHAPTERS = [
    "solve.md",
    "explain.md",
    "probe.md",
    "related.md",
    "compose.md",
    "index.md",
]

SECTIONS = [
    "## 用途",
    "## 前置条件",
    "## 用法 / 参数",
    "## 典型输出",
    "## 导出文件说明",
    "## 端到端完整示例",
]


def test_user_docs_index_links_all_skill_chapters() -> None:
    text = Path("docs/user/README.md").read_text(encoding="utf-8")
    for chapter in CHAPTERS:
        assert f"]({chapter})" in text


def test_user_docs_chapters_follow_template() -> None:
    for chapter in CHAPTERS:
        text = (Path("docs/user") / chapter).read_text(encoding="utf-8")
        for section in SECTIONS:
            assert section in text, f"{chapter} missing {section}"
