from __future__ import annotations

import argparse
from pathlib import Path

from cpho_cli.cli.repl import display
from cpho_cli.cli.repl.commands import Command
from cpho_cli.cli.repl.session import SessionState
from cpho_cli.core.boundary import BoundaryError, ensure_in_workspace
from cpho_cli.core.compose_pdf import assemble_composition_pdfs
from cpho_cli.core.composition import (
    CompositionError,
    load_composition,
    resolve_composition_slots,
    write_composition_template,
)
from cpho_cli.models.composition import CompositionFile, CompositionSlot, SlotSpec


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="/compose", add_help=False)
    sub = parser.add_subparsers(dest="action")
    new = sub.add_parser("new", add_help=False)
    new.add_argument("name")
    new.add_argument("--count", type=int, required=True)
    build = sub.add_parser("build", add_help=False)
    build.add_argument("composition_file")
    build.add_argument("--output")
    auto = sub.add_parser("auto", add_help=False)
    auto.add_argument("--count", type=int, required=True)
    auto.add_argument("--name", default="auto")
    auto.add_argument("--topic")
    auto.add_argument("--tags")
    auto.add_argument("--from", dest="from_source")
    auto.add_argument("--output")
    return parser


async def do_compose(session: SessionState, args: list[str]) -> None:
    try:
        ns = _parser().parse_args(args)
    except SystemExit:
        display.error("用法: /compose new|build|auto ...")
        return
    if ns.action == "new":
        path = write_composition_template(session.workspace_path, name=ns.name, count=ns.count)
        print(f"已创建编排文件: {path}")
        return
    if ns.action == "build":
        await _do_build(session, Path(ns.composition_file), output=_optional_path(ns.output))
        return
    if ns.action == "auto":
        await _do_auto(session, ns)
        return
    display.error("用法: /compose new|build|auto ...")


async def _do_build(session: SessionState, composition_file: Path, *, output: Path | None) -> None:
    try:
        path = ensure_in_workspace(
            session.workspace_path,
            _workspace_relative_path(session.workspace_path, composition_file),
        )
        output_dir = (
            ensure_in_workspace(
                session.workspace_path,
                _workspace_relative_path(session.workspace_path, output),
            )
            if output
            else None
        )
        composition = load_composition(path)
        resolved = resolve_composition_slots(session.workspace_path, composition)
        result = assemble_composition_pdfs(
            session.workspace_path,
            resolved,
            output_dir=output_dir,
            name=composition.name,
        )
    except (BoundaryError, CompositionError, ValueError) as exc:
        display.error(str(exc))
        return
    for warning in result.warnings:
        display.warn(warning)
    print(f"题目卷: {result.problem_pdf}")
    print(f"答案卷: {result.answer_pdf}")


async def _do_auto(session: SessionState, ns: argparse.Namespace) -> None:
    if ns.from_source == "last-related":
        if not session.last_related:
            display.error("last_related 为空，请先运行 /search-related。")
            return
        slots = {
            index: CompositionSlot(problem_id=row.problem_id)
            for index, row in enumerate(session.last_related[: ns.count], start=1)
        }
    else:
        tags = [tag.strip() for tag in ns.tags.split(",") if tag.strip()] if ns.tags else []
        slots = {
            index: CompositionSlot(spec=SlotSpec(topic=ns.topic, tags=tags))
            for index in range(1, ns.count + 1)
        }
    composition = CompositionFile(name=ns.name, slots=slots)
    try:
        output_dir = (
            ensure_in_workspace(
                session.workspace_path,
                _workspace_relative_path(session.workspace_path, Path(ns.output)),
            )
            if ns.output
            else None
        )
        resolved = resolve_composition_slots(session.workspace_path, composition)
        result = assemble_composition_pdfs(
            session.workspace_path,
            resolved,
            output_dir=output_dir,
            name=composition.name,
        )
    except (BoundaryError, CompositionError, ValueError) as exc:
        display.error(str(exc))
        return
    for warning in result.warnings:
        display.warn(warning)
    print(f"题目卷: {result.problem_pdf}")
    print(f"答案卷: {result.answer_pdf}")


def _optional_path(value: str | None) -> Path | None:
    return Path(value) if value else None


def _workspace_relative_path(workspace: Path, path: Path) -> Path:
    return path if path.is_absolute() else workspace / path


def register(registry: dict[str, Command]) -> None:
    registry["/compose"] = Command(
        "/compose",
        "创建或构建组卷编排",
        "/compose new|build|auto ...",
        do_compose,
        category="技能",
    )


__all__ = ["do_compose", "register"]
