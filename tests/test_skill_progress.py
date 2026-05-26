from __future__ import annotations

import io

import pytest

from cpho_cli.core.skill_progress import PlainProgressReporter, wrap_handlers
from cpho_cli.models.skills import SkillStep


def test_plain_progress_wraps_handler_and_prints_elapsed() -> None:
    stream = io.StringIO()
    reporter = PlainProgressReporter(stream=stream)
    step = SkillStep(id="check_each_step", kind="llm", output_keys=["result"])
    handlers = wrap_handlers({"llm": lambda step, values: {"result": "ok"}}, reporter)

    assert handlers["llm"](step, {}) == {"result": "ok"}

    output = stream.getvalue()
    assert "check_each_step" in output
    assert "start" in output
    assert "done" in output
    assert "elapsed=" in output


def test_progress_wrapper_reports_error() -> None:
    stream = io.StringIO()
    reporter = PlainProgressReporter(stream=stream)
    step = SkillStep(id="bad", kind="llm")

    def fail(step, values):  # type: ignore[no-untyped-def]
        raise ValueError("boom")

    handlers = wrap_handlers({"llm": fail}, reporter)

    with pytest.raises(ValueError):
        handlers["llm"](step, {})

    assert "error" in stream.getvalue()
    assert "boom" in stream.getvalue()
