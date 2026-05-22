from pathlib import Path

import pytest

from cpho_cli.core.runtime import SkillRuntime, SkillRuntimeError, redact_secrets
from cpho_cli.models.skills import SkillSpec, SkillStep


def make_spec() -> SkillSpec:
    return SkillSpec(
        name="demo",
        inputs=["a"],
        outputs=["c"],
        steps=[
            SkillStep(id="b", kind="python_tool", input_keys=["a"], output_keys=["b"]),
            SkillStep(id="c", kind="python_tool", input_keys=["b"], output_keys=["c"]),
        ],
    )


def test_blackboard_execution(tmp_path: Path) -> None:
    runtime = SkillRuntime(
        handlers={
            "python_tool": lambda step, values: {
                step.output_keys[0]: values[step.input_keys[0]] + step.id
            }
        },
        trace_path=tmp_path / "trace.jsonl",
    )

    result = runtime.run(make_spec(), {"a": "start-"})

    assert result.blackboard["c"] == "start-bc"
    assert (tmp_path / "trace.jsonl").read_text(encoding="utf-8").count("\n") == 2


def test_missing_key_fails(tmp_path: Path) -> None:
    runtime = SkillRuntime(handlers={"python_tool": lambda step, values: {}})

    with pytest.raises(SkillRuntimeError):
        runtime.run(make_spec(), {})


def test_cycle_fails() -> None:
    spec = SkillSpec(
        name="cycle",
        inputs=["a"],
        outputs=["b"],
        steps=[
            SkillStep(id="a", kind="python_tool", input_keys=["b"], output_keys=["a"]),
            SkillStep(id="b", kind="python_tool", input_keys=["a"], output_keys=["b"]),
        ],
    )
    runtime = SkillRuntime(handlers={"python_tool": lambda step, values: {}})

    with pytest.raises(SkillRuntimeError):
        runtime.run(spec, {"a": "x"})


def test_trace_redacts_secret() -> None:
    assert "sk-secret" not in redact_secrets("token sk-secret", ["sk-secret"])

