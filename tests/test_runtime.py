import json
from pathlib import Path

import pytest

from cpho_cli.core.skill_handlers import make_llm_handler, python_tool_handler
from cpho_cli.core.runtime import SkillRuntime, SkillRuntimeError, redact_secrets
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import LLMResponse
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


def test_python_tool_extracts_problem_and_answer() -> None:
    step = SkillStep(
        id="extract_problem_answer",
        kind="python_tool",
        input_keys=["problem_text", "answer_text"],
        output_keys=["raw_problem", "raw_answer"],
    )

    outputs = python_tool_handler(step, {"problem_text": "p", "answer_text": "a"})

    assert outputs == {"raw_problem": "p", "raw_answer": "a"}


def test_llm_handler_renders_prompt_and_uses_provider(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skill"
    (skill_dir / "prompts").mkdir(parents=True)
    (skill_dir / "prompts" / "normalize.md.j2").write_text(
        "Problem: {{ raw_problem }}",
        encoding="utf-8",
    )

    class FakeProvider:
        messages = None

        def complete(self, messages, params: ModelParams, response_model=None):  # type: ignore[no-untyped-def]
            self.messages = messages
            assert response_model is None
            return LLMResponse(content=json.dumps({"normalized_problem": "clean"}))

    provider = FakeProvider()
    handler = make_llm_handler(provider, ModelParams(name="fake"), skill_dir)
    step = SkillStep(
        id="normalize_problem",
        kind="llm",
        input_keys=["raw_problem"],
        output_keys=["normalized_problem"],
        prompt_template="normalize.md.j2",
    )

    outputs = handler(step, {"raw_problem": "x"})

    assert outputs == {"normalized_problem": "clean"}
    assert provider.messages is not None
    assert provider.messages[-1]["content"] == "Problem: x"


def test_llm_handler_raises_runtime_error_for_missing_output(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skill"
    (skill_dir / "prompts").mkdir(parents=True)
    (skill_dir / "prompts" / "derive.md.j2").write_text(
        "{{ normalized_problem }}",
        encoding="utf-8",
    )

    class FakeProvider:
        def complete(self, messages, params: ModelParams, response_model=None):  # type: ignore[no-untyped-def]
            return LLMResponse(content=json.dumps({"wrong": "value"}))

    handler = make_llm_handler(FakeProvider(), ModelParams(name="fake"), skill_dir)
    runtime = SkillRuntime(handlers={"llm": handler})
    spec = SkillSpec(
        name="missing-output",
        inputs=["normalized_problem"],
        outputs=["subproblem_derivations"],
        steps=[
            SkillStep(
                id="derive_subproblems",
                kind="llm",
                input_keys=["normalized_problem"],
                output_keys=["subproblem_derivations"],
                prompt_template="derive.md.j2",
            )
        ],
    )

    with pytest.raises(SkillRuntimeError, match="missing output keys"):
        runtime.run(spec, {"normalized_problem": "clean"})
