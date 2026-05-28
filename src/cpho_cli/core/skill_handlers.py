from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import jinja2
from pydantic import BaseModel, ValidationError

from cpho_cli.core.json_utils import extract_json_text, loads_json_object
from cpho_cli.core.llm import LLMProvider, LLMProviderError, detect_model_capabilities
from cpho_cli.core.input_routing import choose_input_route
from cpho_cli.core.multimodal import build_multimodal_content
from cpho_cli.core.runtime import SkillRuntimeError, StepHandler
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import ModelCapabilities
from cpho_cli.models.skills import SkillStep
from cpho_cli.models.solve import SolveReport


def _resolve_capabilities(
    provider: LLMProvider,
    params: ModelParams,
    capabilities: ModelCapabilities | None,
) -> ModelCapabilities:
    if capabilities is not None:
        return capabilities
    provider_capabilities = getattr(provider, "capabilities", None)
    if isinstance(provider_capabilities, ModelCapabilities):
        return provider_capabilities
    try:
        return detect_model_capabilities(provider, params.name)
    except LLMProviderError:
        return ModelCapabilities()


def make_llm_handler(
    provider: LLMProvider,
    params: ModelParams,
    skill_dir: Path,
    response_models: Mapping[str, type[BaseModel]] | None = None,
    capabilities: ModelCapabilities | None = None,
) -> StepHandler:
    models_by_output = {"solve_report": SolveReport, **(response_models or {})}
    active_capabilities = _resolve_capabilities(provider, params, capabilities)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(skill_dir / "prompts")),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )

    def handler(step: SkillStep, values: Mapping[str, Any]) -> Mapping[str, Any]:
        if step.prompt_template is None:
            raise SkillRuntimeError(f"Step {step.id} is missing prompt_template")
        try:
            prompt = env.get_template(step.prompt_template).render(**values)
        except jinja2.TemplateError as exc:
            raise SkillRuntimeError(f"Step {step.id} prompt render failed: {exc}") from exc

        output_model = (
            models_by_output.get(step.output_keys[0])
            if len(step.output_keys) == 1
            else None
        )
        content: str | list[dict[str, Any]] = prompt
        file_paths = [
            Path(value)
            for key in ("problem_file", "answer_file")
            if (value := values.get(key)) is not None
        ]
        route = choose_input_route(file_paths, active_capabilities)
        if file_paths:
            content = (
                build_multimodal_content(prompt, route.file_paths, active_capabilities)
                if route.file_paths
                else None
            ) or prompt
        response = provider.complete(
            messages=[
                {
                    "role": "system",
                    "content": "Return strict JSON containing exactly the requested output keys.",
                },
                {"role": "user", "content": content},
            ],
            params=params,
            response_model=output_model,
        )

        if output_model is not None:
            try:
                return {
                    step.output_keys[0]: output_model.model_validate_json(
                        extract_json_text(response.content)
                    )
                }
            except (ValueError, ValidationError) as exc:
                raise SkillRuntimeError(
                    f"Step {step.id} output failed {output_model.__name__} validation: {exc}"
                ) from exc

        try:
            parsed = loads_json_object(response.content)
        except ValueError as exc:
            raise SkillRuntimeError(f"Step {step.id} returned invalid JSON: {exc}") from exc
        if "input_modality_used" in step.output_keys and "input_modality_used" not in parsed:
            parsed["input_modality_used"] = route.input_modality_used
        if "input_routing_warning" in step.output_keys and "input_routing_warning" not in parsed:
            parsed["input_routing_warning"] = route.warning
        missing = [key for key in step.output_keys if key not in parsed]
        if missing:
            raise SkillRuntimeError(f"Step {step.id} missing output keys: {missing}")
        return {key: parsed[key] for key in step.output_keys}

    return handler


def python_tool_handler(step: SkillStep, values: Mapping[str, Any]) -> Mapping[str, Any]:
    if step.id != "extract_problem_answer":
        raise SkillRuntimeError(f"Unsupported python_tool step: {step.id}")
    return {
        "raw_problem": values["problem_text"],
        "raw_answer": values["answer_text"],
    }
