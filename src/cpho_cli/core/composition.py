from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from cpho_cli.core.index.api import get_problem_entry
from cpho_cli.core.index.compose import compose_problem_list
from cpho_cli.models.composition import CompositionFile
from cpho_cli.models.index import IndexEntry


class CompositionError(RuntimeError):
    """Raised when a composition file or slot cannot be resolved."""


@dataclass(frozen=True)
class ResolvedCompositionSlot:
    slot: int
    problem_id: str | None
    entry: IndexEntry | None
    is_pass: bool = False


def default_composition_path(workspace: Path, name: str) -> Path:
    return workspace / ".cpho" / "compositions" / f"{name}.yml"


def load_composition(path: Path) -> CompositionFile:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return CompositionFile.model_validate(raw)
    except (yaml.YAMLError, ValidationError) as exc:
        raise ValueError(f"编排文件无效：{exc}") from exc


def write_composition_template(workspace: Path, *, name: str, count: int) -> Path:
    path = default_composition_path(workspace, name)
    data: dict[str, Any] = {
        "name": name,
        "slots": {
            index: {
                "spec": {
                    "topic": None,
                    "tags": [],
                    "requirement": None,
                }
            }
            for index in range(1, count + 1)
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def resolve_composition_slots(
    workspace: Path,
    composition: CompositionFile,
) -> list[ResolvedCompositionSlot]:
    resolved: list[ResolvedCompositionSlot] = []
    used_problem_ids: set[str] = set()
    for slot_number in sorted(composition.slots):
        slot = composition.slots[slot_number]
        if slot.pass_slot:
            resolved.append(
                ResolvedCompositionSlot(
                    slot=slot_number,
                    problem_id=None,
                    entry=None,
                    is_pass=True,
                )
            )
            continue
        if slot.problem_id is not None:
            entry = get_problem_entry(workspace, slot.problem_id)
            if entry is None:
                raise CompositionError(f"找不到 slot {slot_number} 指定题目：{slot.problem_id}")
            if entry.problem_id in used_problem_ids:
                raise CompositionError(f"重复题目：{entry.problem_id}")
            used_problem_ids.add(entry.problem_id)
            resolved.append(
                ResolvedCompositionSlot(
                    slot=slot_number,
                    problem_id=entry.problem_id,
                    entry=entry,
                )
            )
            continue
        if slot.spec is None:
            raise CompositionError(f"slot {slot_number} 缺少 spec")
        candidates = compose_problem_list(
            workspace,
            topic_path=slot.spec.topic,
            tag_ids=slot.spec.tags,
        )
        candidates = [entry for entry in candidates if entry.problem_id not in used_problem_ids]
        if not candidates:
            raise CompositionError(f"找不到符合 slot {slot_number} 的题目")
        entry = candidates[0]
        used_problem_ids.add(entry.problem_id)
        resolved.append(
            ResolvedCompositionSlot(
                slot=slot_number,
                problem_id=entry.problem_id,
                entry=entry,
            )
        )
    return resolved


__all__ = [
    "CompositionError",
    "ResolvedCompositionSlot",
    "default_composition_path",
    "load_composition",
    "resolve_composition_slots",
    "write_composition_template",
]
