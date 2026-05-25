from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
import jinja2
from pydantic import Field, ValidationError

from cpho_cli.core.config import resolve_model_params
from cpho_cli.core.index import IndexBuildError
from cpho_cli.core.index.vocabulary import normalize_alias
from cpho_cli.core.llm import LLMProvider, create_llm_provider
from cpho_cli.core.runtime import redact_secrets
from cpho_cli.models.config import AppConfig, ResolvedProviderConfig, StrictModel
from cpho_cli.models.index import (
    CandidateTag,
    CanonicalTag,
    TaggedReference,
    TagCategory,
    TagSource,
    TagStatus,
    Vocabulary,
)
from cpho_cli.models.runtime import TraceRecord


SYSTEM_PROMPT = (
    "你是物理竞赛题目标签归一化助手。给定题目 OCR 文本和受控词表，"
    "从受控词表中选出最匹配的 canonical tag internal_id。"
    "严格仅从提供的 internal_id 列表中选择。"
    "如果发现需要的概念不在列表里，仅在 candidates 数组里提议新 tag，不要编造词表外的 id 放入 selected_* 字段。"
)


class CandidateTagSuggestion(StrictModel):
    internal_id_suggestion: str
    display_zh_suggestion: str
    category: TagCategory
    proposed_aliases: list[str] = Field(default_factory=list)
    rationale: str


class TagRefinementOutput(StrictModel):
    selected_physics_models: list[str] = Field(default_factory=list)
    selected_math_techniques: list[str] = Field(default_factory=list)
    selected_heuristics: list[str] = Field(default_factory=list)
    difficulty_aspects: list[str] = Field(default_factory=list)
    candidates: list[CandidateTagSuggestion] = Field(default_factory=list)


class CanonicalMappingResult(StrictModel):
    physics_model_tags: list[TaggedReference] = Field(default_factory=list)
    math_technique_tags: list[TaggedReference] = Field(default_factory=list)
    heuristic_tags: list[TaggedReference] = Field(default_factory=list)
    difficulty_aspects: list[str] = Field(default_factory=list)
    candidates: list[CandidateTag] = Field(default_factory=list)


def _prompts_dir() -> Path:
    return Path(__file__).parent / "prompts"


def load_tag_prompt_version() -> str:
    data = yaml.safe_load((_prompts_dir() / "MANIFEST.yml").read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise IndexBuildError("Tag prompt manifest must be a YAML mapping.")
    version = data.get("version")
    if not isinstance(version, str):
        raise IndexBuildError("Tag prompt manifest is missing a string version.")
    return version


def _build_jinja_env() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(_prompts_dir())),
        undefined=jinja2.StrictUndefined,
        autoescape=False,
    )


def append_trace(trace_path: Path, record: TraceRecord, secrets: list[str]) -> None:
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    text = record.model_dump_json()
    text = redact_secrets(text, secrets)
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(text + "\n")


def _render_user_prompt(
    problem_id: str,
    problem_text: str,
    vocabulary: Vocabulary,
) -> str:
    env = _build_jinja_env()
    template = env.get_template("tag_refinement.md.j2")
    controlled_vocabulary: list[dict[str, Any]] = [
        {
            "internal_id": tag.internal_id,
            "category": tag.category.value,
            "display_zh": tag.display_zh,
            "aliases": tag.aliases,
        }
        for tag in vocabulary.tags.values()
    ]
    return template.render(
        problem_id=problem_id,
        problem_text=problem_text[:3000],
        controlled_vocabulary=controlled_vocabulary,
    )


def _candidate_from_suggestion(
    suggestion: CandidateTagSuggestion,
    problem_id: str,
    now: datetime,
) -> CandidateTag:
    return CandidateTag(
        internal_id_suggestion=suggestion.internal_id_suggestion,
        display_zh_suggestion=suggestion.display_zh_suggestion,
        category=suggestion.category,
        proposed_aliases=suggestion.proposed_aliases,
        rationale=suggestion.rationale,
        first_seen_problem_id=problem_id,
        first_seen_at=now,
        occurrences=1,
        status=TagStatus.CANDIDATE,
    )


def _fabricated_id_candidate(
    internal_id: str,
    category: TagCategory,
    bucket_name: str,
    problem_id: str,
    now: datetime,
) -> CandidateTag:
    return CandidateTag(
        internal_id_suggestion=internal_id,
        display_zh_suggestion=internal_id,
        category=category,
        proposed_aliases=[],
        rationale=(
            f"LLM emitted id '{internal_id}' for {bucket_name} but it is not in the "
            "controlled vocabulary."
        ),
        first_seen_problem_id=problem_id,
        first_seen_at=now,
        occurrences=1,
        status=TagStatus.CANDIDATE,
    )


def _resolve_canonical_tag(
    raw_id: str,
    vocabulary: Vocabulary,
    allowed_categories: set[TagCategory],
) -> CanonicalTag | None:
    direct = vocabulary.tags.get(raw_id)
    if direct is not None and direct.category in allowed_categories:
        return direct

    alias_id = vocabulary.alias_index.get(normalize_alias(raw_id))
    if alias_id is None:
        return None
    alias_match = vocabulary.tags.get(alias_id)
    if alias_match is not None and alias_match.category in allowed_categories:
        return alias_match
    return None


def _map_bucket(
    raw_ids: list[str],
    vocabulary: Vocabulary,
    allowed_categories: set[TagCategory],
    primary_category: TagCategory,
    bucket_name: str,
    source: TagSource,
    problem_id: str,
    now: datetime,
) -> tuple[list[TaggedReference], list[CandidateTag]]:
    references: list[TaggedReference] = []
    candidates: list[CandidateTag] = []
    seen: set[str] = set()
    for raw_id in raw_ids:
        tag = _resolve_canonical_tag(raw_id, vocabulary, allowed_categories)
        if tag is None:
            candidates.append(
                _fabricated_id_candidate(raw_id, primary_category, bucket_name, problem_id, now)
            )
            continue
        if tag.internal_id in seen:
            continue
        seen.add(tag.internal_id)
        references.append(
            TaggedReference(internal_id=tag.internal_id, source=source, confidence=None)
        )
    return references, candidates


def canonical_mapping_pass(
    llm_output: TagRefinementOutput,
    vocabulary: Vocabulary,
    problem_id: str,
    source: TagSource,
) -> CanonicalMappingResult:
    """Map LLM output into controlled vocabulary references.

    Guarantees: only Vocabulary internal_ids reach IndexEntry fields; aliases are
    resolved before rejection; category misassignment produces a candidate, not a
    silent re-bucket.
    """
    now = datetime.now(timezone.utc)
    physics_tags, physics_candidates = _map_bucket(
        llm_output.selected_physics_models,
        vocabulary,
        {TagCategory.PHYSICS_LAW, TagCategory.PHYSICS_MODEL},
        TagCategory.PHYSICS_MODEL,
        "selected_physics_models",
        source,
        problem_id,
        now,
    )
    math_tags, math_candidates = _map_bucket(
        llm_output.selected_math_techniques,
        vocabulary,
        {TagCategory.MATH_TECHNIQUE},
        TagCategory.MATH_TECHNIQUE,
        "selected_math_techniques",
        source,
        problem_id,
        now,
    )
    heuristic_tags, heuristic_candidates = _map_bucket(
        llm_output.selected_heuristics,
        vocabulary,
        {TagCategory.HEURISTIC, TagCategory.APPROXIMATION},
        TagCategory.HEURISTIC,
        "selected_heuristics",
        source,
        problem_id,
        now,
    )
    suggested_candidates = [
        _candidate_from_suggestion(candidate, problem_id, now) for candidate in llm_output.candidates
    ]

    return CanonicalMappingResult(
        physics_model_tags=physics_tags,
        math_technique_tags=math_tags,
        heuristic_tags=heuristic_tags,
        difficulty_aspects=llm_output.difficulty_aspects,
        candidates=[
            *physics_candidates,
            *math_candidates,
            *heuristic_candidates,
            *suggested_candidates,
        ],
    )


def refine_tags(
    problem_id: str,
    ocr_text: str,
    vocabulary: Vocabulary,
    config: AppConfig,
    provider_config: ResolvedProviderConfig,
    llm_provider: LLMProvider | None = None,
    trace_path: Path | None = None,
    source: TagSource = TagSource.OCR_FALLBACK,
) -> CanonicalMappingResult:
    started = datetime.now(timezone.utc)
    provider = llm_provider or create_llm_provider(
        kind=provider_config.kind,
        api_key=provider_config.api_key,
        base_url=provider_config.base_url,
        timeout=provider_config.timeout,
    )
    params = resolve_model_params(config, "index", provider_name=provider_config.name)
    user_prompt = _render_user_prompt(problem_id, ocr_text, vocabulary)
    input_keys = ["ocr_text", f"vocabulary_{vocabulary.version}"]
    output_keys = ["tag_refinement"]

    try:
        response = provider.complete(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            params=params,
            response_model=TagRefinementOutput,
        )
        try:
            llm_output = TagRefinementOutput.model_validate_json(response.content)
        except ValidationError as exc:
            raise IndexBuildError(
                f"LLM response failed TagRefinementOutput validation: {exc}"
            ) from exc
        result = canonical_mapping_pass(llm_output, vocabulary, problem_id, source)
        if trace_path is not None:
            append_trace(
                trace_path,
                TraceRecord(
                    step_id=f"tag_{problem_id}",
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
        return result
    except Exception as exc:
        if trace_path is not None:
            append_trace(
                trace_path,
                TraceRecord(
                    step_id=f"tag_{problem_id}",
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
