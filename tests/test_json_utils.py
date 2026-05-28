from __future__ import annotations

import pytest

from cpho_cli.core.json_utils import extract_json_text, loads_json_object


def test_extract_json_text_accepts_fenced_json() -> None:
    assert extract_json_text('```json\n{"x": 1}\n```') == '{"x": 1}'


def test_loads_json_object_rejects_non_object() -> None:
    with pytest.raises(ValueError, match="must be an object"):
        loads_json_object("[1, 2, 3]")


def test_loads_json_object_returns_dict() -> None:
    assert loads_json_object('```json\n{"x": 1}\n```') == {"x": 1}
