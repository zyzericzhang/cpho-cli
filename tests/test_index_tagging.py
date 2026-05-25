from __future__ import annotations

import json
from pathlib import Path

import pytest

from cpho_cli.core.index import IndexBuildError
from cpho_cli.core.index.tagging import (
    TagRefinementOutput,
    load_tag_prompt_version,
    refine_tags,
)
from cpho_cli.core.index.vocabulary import normalize_alias
from cpho_cli.models.config import AppConfig, ModelParams, ResolvedProviderConfig, SkillConfig
from cpho_cli.models.index import CanonicalTag, TagCategory, TagSource, Vocabulary
from cpho_cli.models.llm import LLMResponse, LLMUsage


class FakeLLMProvider:
    def __init__(
        self,
        response_payload: TagRefinementOutput | None = None,
        raise_with: str | None = None,
        raw_content: str | None = None,
    ) -> None:
        self.response_payload = response_payload
        self.raise_with = raise_with
        self.raw_content = raw_content
        self.last_messages: list[dict[str, str]] | None = None
        self.last_params: ModelParams | None = None
        self.last_response_model_name: str | None = None

    def complete(
        self,
        messages: list[dict[str, str]],
        params: ModelParams,
        response_model: type[TagRefinementOutput] | None = None,
    ) -> LLMResponse:
        self.last_messages = messages
        self.last_params = params
        self.last_response_model_name = response_model.__name__ if response_model else None
        if self.raise_with:
            raise RuntimeError(self.raise_with)
        if self.raw_content is not None:
            return LLMResponse(content=self.raw_content, usage=LLMUsage())
        assert self.response_payload is not None
        return LLMResponse(content=self.response_payload.model_dump_json(), usage=LLMUsage())


def _provider_config(api_key: str = "sk-test") -> ResolvedProviderConfig:
    return ResolvedProviderConfig(
        name="openrouter",
        kind="openrouter",
        api_key=api_key,
        base_url="https://x.test",
    )


def _vocab() -> Vocabulary:
    tag = CanonicalTag(
        internal_id="newton_second_law",
        display_zh="牛顿第二定律",
        category=TagCategory.PHYSICS_MODEL,
        aliases=["F=ma"],
    )
    return Vocabulary(
        version="test",
        tags={tag.internal_id: tag},
        alias_index={
            normalize_alias(label): tag.internal_id
            for label in [tag.internal_id, tag.display_zh, *tag.aliases]
        },
    )


def _refine(
    fake: FakeLLMProvider,
    tmp_path: Path,
    *,
    config: AppConfig | None = None,
    trace_path: Path | None = None,
    ocr_text: str = "Use F=ma.",
    provider_config: ResolvedProviderConfig | None = None,
):
    return refine_tags(
        problem_id="p1",
        ocr_text=ocr_text,
        vocabulary=_vocab(),
        config=config or AppConfig(),
        provider_config=provider_config or _provider_config(),
        llm_provider=fake,
        trace_path=trace_path,
    )


def test_refine_tags_calls_provider_with_response_model(tmp_path: Path) -> None:
    fake = FakeLLMProvider(TagRefinementOutput())

    _refine(fake, tmp_path)

    assert fake.last_response_model_name == "TagRefinementOutput"


def test_refine_tags_calls_provider_with_resolve_model_params_index_skill(
    tmp_path: Path,
) -> None:
    fake = FakeLLMProvider(TagRefinementOutput())
    config = AppConfig(skills={"index": SkillConfig(model=ModelParams(temperature=0.0))})

    _refine(fake, tmp_path, config=config)

    assert fake.last_params is not None
    assert fake.last_params.temperature == 0.0


def test_refine_tags_uses_llm_provider_module_not_direct_httpx() -> None:
    source = Path("src/cpho_cli/core/index/tagging.py").read_text(encoding="utf-8")
    non_comment_lines = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )

    assert "httpx" not in non_comment_lines


def test_refine_tags_no_fstring_prompt() -> None:
    source = Path("src/cpho_cli/core/index/tagging.py").read_text(encoding="utf-8")

    assert 'f"Problem' not in source
    assert "tag_refinement.md.j2" in source


def test_refine_tags_writes_trace_when_path_given(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.jsonl"
    fake = FakeLLMProvider(TagRefinementOutput())

    _refine(fake, tmp_path, trace_path=trace_path)

    record = json.loads(trace_path.read_text(encoding="utf-8"))
    assert record["step_id"] == "tag_p1"
    assert record["status"] == "passed"
    assert "ocr_text" in record["input_keys"]


def test_refine_tags_skips_trace_when_path_none(tmp_path: Path) -> None:
    fake = FakeLLMProvider(TagRefinementOutput())

    _refine(fake, tmp_path, trace_path=None)

    assert list(tmp_path.iterdir()) == []


def test_trace_redacts_api_key(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.jsonl"
    api_key = "sk-secret-key-123"
    fake = FakeLLMProvider(raise_with=f"provider failed with {api_key}")

    with pytest.raises(RuntimeError):
        _refine(
            fake,
            tmp_path,
            trace_path=trace_path,
            provider_config=_provider_config(api_key),
        )

    text = trace_path.read_text(encoding="utf-8")
    assert api_key not in text
    assert "[REDACTED]" in text


def test_refine_tags_validation_error_raises_index_build_error(tmp_path: Path) -> None:
    fake = FakeLLMProvider(raw_content='{"invalid": "json that does not match schema"}')

    with pytest.raises(IndexBuildError):
        _refine(fake, tmp_path)


def test_refine_tags_truncates_long_ocr_text(tmp_path: Path) -> None:
    fake = FakeLLMProvider(TagRefinementOutput())

    _refine(fake, tmp_path, ocr_text="x" * 10000)

    assert fake.last_messages is not None
    assert len(fake.last_messages[1]["content"]) < 6000


def test_refine_tags_canonical_mapping_integrated(tmp_path: Path) -> None:
    fake = FakeLLMProvider(
        TagRefinementOutput(selected_physics_models=["newton_second_law"])
    )

    result = _refine(fake, tmp_path)

    assert [tag.internal_id for tag in result.physics_model_tags] == ["newton_second_law"]
    assert result.physics_model_tags[0].source is TagSource.OCR_FALLBACK


def test_refine_tags_prompt_uses_ocr_and_vocabulary_only(tmp_path: Path) -> None:
    fake = FakeLLMProvider(TagRefinementOutput())

    _refine(fake, tmp_path)

    assert fake.last_messages is not None
    prompt = fake.last_messages[1]["content"]
    assert "Solve" + "Report" not in prompt
    assert "solve_report" not in prompt
    assert "newton_second_law" in prompt
    assert "Use F=ma." in prompt


def test_load_tag_prompt_version_reads_manifest() -> None:
    assert load_tag_prompt_version() == "v2"
