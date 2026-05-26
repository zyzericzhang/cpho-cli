from __future__ import annotations

from pathlib import Path


def test_extension_docs_mark_out_of_scope_and_show_python_example() -> None:
    text = Path("docs/user/extensions.md").read_text(encoding="utf-8")
    for phrase in [
        "不支持",
        "YAML 配置式 skill",
        "自然语言生成 skill",
        "pip 安装第三方 skill",
        "core/llm.py",
        "core/index/api.py",
        "register(registry)",
        "/count",
    ]:
        assert phrase in text


def test_examples_exist_and_are_documented() -> None:
    for path in [
        "examples/README.md",
        "examples/sample-problem.md",
        "examples/sample-answer.md",
    ]:
        assert Path(path).is_file(), path
    assert "替换为自己的题库目录" in Path("examples/README.md").read_text(encoding="utf-8")
