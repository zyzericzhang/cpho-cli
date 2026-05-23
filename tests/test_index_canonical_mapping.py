from __future__ import annotations

from cpho_cli.core.index.vocabulary import normalize_alias
from cpho_cli.core.index.tagging import (
    CandidateTagSuggestion,
    TagRefinementOutput,
    canonical_mapping_pass,
)
from cpho_cli.models.index import CanonicalTag, TagCategory, TagSource, TagStatus, Vocabulary


def _vocab(*tag_specs: tuple[str, str, TagCategory, list[str]]) -> Vocabulary:
    tags = {
        spec[0]: CanonicalTag(
            internal_id=spec[0],
            display_zh=spec[1],
            category=spec[2],
            aliases=spec[3] if len(spec) > 3 else [],
        )
        for spec in tag_specs
    }
    return Vocabulary(
        version="test",
        tags=tags,
        alias_index={
            normalize_alias(label): tag.internal_id
            for tag in tags.values()
            for label in [tag.internal_id, tag.display_zh, *tag.aliases]
        },
    )


def _candidate_summary(candidates):  # type: ignore[no-untyped-def]
    return [
        (
            candidate.internal_id_suggestion,
            candidate.display_zh_suggestion,
            candidate.category,
            candidate.proposed_aliases,
            candidate.rationale,
            candidate.first_seen_problem_id,
            candidate.occurrences,
            candidate.status,
        )
        for candidate in candidates
    ]


def test_known_internal_id_passes_through() -> None:
    vocab = _vocab(("newton_second_law", "牛顿第二定律", TagCategory.PHYSICS_MODEL, []))
    output = TagRefinementOutput(selected_physics_models=["newton_second_law"])

    result = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    assert [tag.internal_id for tag in result.physics_model_tags] == ["newton_second_law"]
    assert result.physics_model_tags[0].source is TagSource.SOLVE_REPORT


def test_physics_bucket_accepts_law_and_model_categories() -> None:
    vocab = _vocab(
        ("momentum_conservation", "动量守恒", TagCategory.PHYSICS_LAW, []),
        ("rainbow_scattering_model", "虹散射模型", TagCategory.PHYSICS_MODEL, []),
    )
    output = TagRefinementOutput(
        selected_physics_models=["momentum_conservation", "rainbow_scattering_model"]
    )

    result = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    assert [tag.internal_id for tag in result.physics_model_tags] == [
        "momentum_conservation",
        "rainbow_scattering_model",
    ]
    assert result.candidates == []


def test_unknown_internal_id_becomes_candidate() -> None:
    vocab = _vocab(("newton_second_law", "牛顿第二定律", TagCategory.PHYSICS_MODEL, []))
    output = TagRefinementOutput(selected_physics_models=["newton_third_law"])

    result = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    assert result.physics_model_tags == []
    assert len(result.candidates) == 1
    assert result.candidates[0].internal_id_suggestion == "newton_third_law"
    assert result.candidates[0].status is TagStatus.CANDIDATE


def test_alias_resolved_to_canonical() -> None:
    vocab = _vocab(("newton_second_law", "牛顿第二定律", TagCategory.PHYSICS_MODEL, ["F=ma"]))
    output = TagRefinementOutput(selected_physics_models=["F=ma"])

    result = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    assert [tag.internal_id for tag in result.physics_model_tags] == ["newton_second_law"]


def test_chinese_alias_resolved() -> None:
    vocab = _vocab(
        ("newton_second_law", "牛顿第二定律", TagCategory.PHYSICS_MODEL, ["牛顿第二"])
    )
    output = TagRefinementOutput(selected_physics_models=["牛顿第二"])

    result = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    assert [tag.internal_id for tag in result.physics_model_tags] == ["newton_second_law"]


def test_category_misassignment_becomes_candidate() -> None:
    vocab = _vocab(("newton_second_law", "牛顿第二定律", TagCategory.PHYSICS_MODEL, []))
    output = TagRefinementOutput(selected_math_techniques=["newton_second_law"])

    result = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    assert result.physics_model_tags == []
    assert result.math_technique_tags == []
    assert len(result.candidates) == 1
    assert result.candidates[0].internal_id_suggestion == "newton_second_law"


def test_heuristics_bucket_accepts_two_categories() -> None:
    vocab = _vocab(
        ("approximation_to_first_order", "一阶近似", TagCategory.APPROXIMATION, []),
        ("free_body_diagram", "受力图", TagCategory.HEURISTIC, []),
    )
    output = TagRefinementOutput(
        selected_heuristics=["approximation_to_first_order", "free_body_diagram"]
    )

    result = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    assert [tag.internal_id for tag in result.heuristic_tags] == [
        "approximation_to_first_order",
        "free_body_diagram",
    ]


def test_duplicate_ids_within_bucket_deduplicated() -> None:
    vocab = _vocab(("newton_second_law", "牛顿第二定律", TagCategory.PHYSICS_MODEL, []))
    output = TagRefinementOutput(
        selected_physics_models=["newton_second_law", "newton_second_law"]
    )

    result = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    assert [tag.internal_id for tag in result.physics_model_tags] == ["newton_second_law"]


def test_llm_candidates_passed_through_with_metadata() -> None:
    vocab = _vocab(("newton_second_law", "牛顿第二定律", TagCategory.PHYSICS_MODEL, []))
    output = TagRefinementOutput(
        candidates=[
            CandidateTagSuggestion(
                internal_id_suggestion="energy_method",
                display_zh_suggestion="能量法",
                category=TagCategory.HEURISTIC,
                proposed_aliases=["energy"],
                rationale="词表缺少能量法。",
            )
        ]
    )

    result = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    assert len(result.candidates) == 1
    assert result.candidates[0].occurrences == 1
    assert result.candidates[0].first_seen_problem_id == "p1"
    assert result.candidates[0].status is TagStatus.CANDIDATE


def test_difficulty_aspects_passed_through_unchanged() -> None:
    aspects = ["选系统时容易忽略约束", "近似展开到二阶非显然"]
    result = canonical_mapping_pass(
        TagRefinementOutput(difficulty_aspects=aspects),
        _vocab(("newton_second_law", "牛顿第二定律", TagCategory.PHYSICS_MODEL, [])),
        "p1",
        TagSource.SOLVE_REPORT,
    )

    assert result.difficulty_aspects == aspects


def test_canonical_mapping_pass_deterministic() -> None:
    vocab = _vocab(("newton_second_law", "牛顿第二定律", TagCategory.PHYSICS_MODEL, ["F=ma"]))
    output = TagRefinementOutput(
        selected_physics_models=["F=ma", "fabricated_id"],
        difficulty_aspects=["难点"],
    )

    result1 = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)
    result2 = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    assert result1.physics_model_tags == result2.physics_model_tags
    assert result1.math_technique_tags == result2.math_technique_tags
    assert result1.heuristic_tags == result2.heuristic_tags
    assert result1.difficulty_aspects == result2.difficulty_aspects
    assert _candidate_summary(result1.candidates) == _candidate_summary(result2.candidates)


def test_source_tag_propagates() -> None:
    vocab = _vocab(
        ("newton_second_law", "牛顿第二定律", TagCategory.PHYSICS_MODEL, []),
        ("algebraic_substitution", "代数代换", TagCategory.MATH_TECHNIQUE, []),
        ("free_body_diagram", "受力图", TagCategory.HEURISTIC, []),
    )
    output = TagRefinementOutput(
        selected_physics_models=["newton_second_law"],
        selected_math_techniques=["algebraic_substitution"],
        selected_heuristics=["free_body_diagram"],
    )

    fallback_result = canonical_mapping_pass(output, vocab, "p1", TagSource.OCR_FALLBACK)
    solve_result = canonical_mapping_pass(output, vocab, "p1", TagSource.SOLVE_REPORT)

    fallback_refs = (
        fallback_result.physics_model_tags
        + fallback_result.math_technique_tags
        + fallback_result.heuristic_tags
    )
    solve_refs = (
        solve_result.physics_model_tags
        + solve_result.math_technique_tags
        + solve_result.heuristic_tags
    )
    assert {tag.source for tag in fallback_refs} == {TagSource.OCR_FALLBACK}
    assert {tag.source for tag in solve_refs} == {TagSource.SOLVE_REPORT}
