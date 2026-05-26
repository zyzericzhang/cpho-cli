from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.cli.repl.app import ReplApp
from cpho_cli.cli.repl.commands import Command


@pytest.mark.asyncio
async def test_criterion_help_lists_phase02_2_commands(
    repl_workspace_with_index: tuple[Path, list[str]],
    capsys,
) -> None:
    workspace, _ = repl_workspace_with_index
    app = ReplApp(workspace=workspace)

    await app.dispatch("/help")

    output = capsys.readouterr().out
    for name in [
        "/search",
        "/show",
        "/workspace",
        "/status",
        "/config",
        "/index",
        "/reload-index",
        "/resume",
        "/help",
        "/set",
        "/run",
        "/solve",
        "/explain",
        "/probe",
    ]:
        assert name in output
    assert "/quiz" not in output


@pytest.mark.asyncio
async def test_criterion_search_show_loop(
    repl_workspace_with_index: tuple[Path, list[str]],
    capsys,
) -> None:
    workspace, ids = repl_workspace_with_index
    app = ReplApp(workspace=workspace)

    await app.dispatch("/search --physics-model newton_second_law")
    await app.dispatch("/show 1")

    output = capsys.readouterr().out
    assert app.session.last_search_result_ids == [ids[0]]
    assert app.session.current_problem_id == ids[0]
    assert "牛顿第二定律" in output


def test_structural_no_cmd2_and_no_core_prompt_toolkit() -> None:
    root = Path("src/cpho_cli")
    repl_text = "\n".join(path.read_text(encoding="utf-8") for path in (root / "cli" / "repl").rglob("*.py"))
    core_text = "\n".join(path.read_text(encoding="utf-8") for path in (root / "core").rglob("*.py"))

    assert "import cmd2" not in repl_text
    assert "from cmd2" not in repl_text
    assert "prompt_toolkit" not in core_text


@pytest.mark.asyncio
async def test_fake_command_appears_without_runtime_change(tmp_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    app = ReplApp(workspace=tmp_path)

    async def fake(session, args: list[str]) -> None:  # type: ignore[no-untyped-def]
        print("fake")

    app.registry["/fake"] = Command("/fake", "假命令", "/fake", fake, category="测试")
    setattr(app.session, "registry", app.registry)

    await app.dispatch("/help")

    assert "/fake" in capsys.readouterr().out
