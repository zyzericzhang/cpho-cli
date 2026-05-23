"""LLM-based topic classification for physics problems."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from cpho_cli.core.config import resolve_model_params
from cpho_cli.core.index import IndexBuildError
from cpho_cli.core.index.tagging import _build_jinja_env, append_trace
from cpho_cli.core.llm import LLMProvider, OpenRouterProvider
from cpho_cli.core.runtime import redact_secrets
from cpho_cli.models.config import AppConfig, ResolvedProviderConfig, StrictModel
from cpho_cli.models.runtime import TraceRecord
from cpho_cli.models.topic import TopicTaxonomy

TOPIC_SYSTEM_PROMPT = (
    "你是物理竞赛题目分类助手。给定题目文本和完整的主题分类树，选出最匹配的一个主题路径。"
    "只能选择提供列表中存在的路径，不能自创。"
)


class TopicAssignmentOutput(StrictModel):
    topic_path: str
    confidence: float | None = None
    rationale: str


def _render_topic_prompt(
    problem_id: str,
    problem_text: str,
    taxonomy: TopicTaxonomy,
) -> str:
    env = _build_jinja_env()
    template = env.get_template("topic_assignment.md.j2")
    return template.render(
        problem_id=problem_id,
        problem_text=problem_text[:3000],
        valid_paths=taxonomy.flatten_paths(),
    )


def assign_topic(
    problem_id: str,
    ocr_text: str,
    taxonomy: TopicTaxonomy,
    config: AppConfig,
    provider_config: ResolvedProviderConfig,
    llm_provider: LLMProvider | None = None,
    trace_path: Path | None = None,
) -> TopicAssignmentOutput:
    """Assign a single topic path to a problem via LLM classification."""
    started = datetime.now(timezone.utc)
    provider = llm_provider or OpenRouterProvider(
        api_key=provider_config.api_key,
        base_url=provider_config.base_url,
    )
    params = resolve_model_params(config, "index")
    user_prompt = _render_topic_prompt(problem_id, ocr_text, taxonomy)
    input_keys = ["ocr_text", f"taxonomy_{taxonomy.version}"]
    output_keys = ["topic_assignment"]

    try:
        response = provider.complete(
            messages=[
                {"role": "system", "content": TOPIC_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            params=params,
            response_model=TopicAssignmentOutput,
        )
        try:
            output = TopicAssignmentOutput.model_validate_json(response.content)
        except ValidationError as exc:
            raise IndexBuildError(
                f"LLM response failed TopicAssignmentOutput validation: {exc}"
            ) from exc

        if taxonomy.find_node_by_path(output.topic_path) is None:
            raise IndexBuildError(
                f"LLM returned invalid topic path: {output.topic_path!r}"
            )

        if trace_path is not None:
            append_trace(
                trace_path,
                TraceRecord(
                    step_id=f"topic_{problem_id}",
                    status="passed",
                    input_keys=input_keys,
                    output_keys=output_keys,
                    retry_count=0,
                    started_at=started,
                    finished_at=datetime.now(timezone.utc),
                    error=None,
                ),
                [provider_config.api_key],
            )
        return output
    except Exception as exc:
        if trace_path is not None:
            append_trace(
                trace_path,
                TraceRecord(
                    step_id=f"topic_{problem_id}",
                    status="failed",
                    input_keys=input_keys,
                    output_keys=output_keys,
                    retry_count=0,
                    started_at=started,
                    finished_at=datetime.now(timezone.utc),
                    error=redact_secrets(str(exc), [provider_config.api_key]),
                ),
                [provider_config.api_key],
            )
        raise
