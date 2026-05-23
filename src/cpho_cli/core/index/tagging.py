from __future__ import annotations

from datetime import datetime, timezone

from pydantic import Field

from cpho_cli.core.index.vocabulary import normalize_alias
from cpho_cli.models.config import StrictModel
from cpho_cli.models.index import (
    CandidateTag,
    CanonicalTag,
    TaggedReference,
    TagCategory,
    TagSource,
    TagStatus,
    Vocabulary,
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
