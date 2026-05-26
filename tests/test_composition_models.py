from __future__ import annotations

from pathlib import Path

import pytest

from cpho_cli.core.composition import load_composition, write_composition_template
from cpho_cli.models.composition import CompositionFile


def test_load_composition_validates_three_way_slot_schema(tmp_path: Path) -> None:
    path = tmp_path / "set.yml"
    path.write_text(
        """
name: set
slots:
  1:
    problem_id: p1
  2:
    pass: true
  3:
    spec:
      topic: 力学
      tags: [newton]
      requirement: 中等难度
""",
        encoding="utf-8",
    )

    composition = load_composition(path)

    assert composition.name == "set"
    assert composition.slots[1].problem_id == "p1"
    assert composition.slots[2].pass_slot is True
    assert composition.slots[3].spec is not None


def test_load_composition_rejects_mixed_slot_modes(tmp_path: Path) -> None:
    path = tmp_path / "bad.yml"
    path.write_text(
        """
name: bad
slots:
  1:
    problem_id: p1
    pass: true
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="三选一"):
        load_composition(path)


def test_write_composition_template_is_valid_yaml(tmp_path: Path) -> None:
    path = write_composition_template(tmp_path, name="mock", count=2)

    composition = load_composition(path)

    assert path == tmp_path / ".cpho" / "compositions" / "mock.yml"
    assert isinstance(composition, CompositionFile)
    assert sorted(composition.slots) == [1, 2]
