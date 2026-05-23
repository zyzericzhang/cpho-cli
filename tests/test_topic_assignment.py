from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from cpho_cli.core.index import IndexBuildError
from cpho_cli.core.index.topic_assignment import (
    TopicAssignmentOutput,
    _render_topic_prompt,
    assign_topic,
)
from cpho_cli.models.config import AppConfig, ModelParams, ResolvedProviderConfig
from cpho_cli.models.llm import LLMResponse, LLMUsage
from cpho_cli.models.topic import TopicNode, TopicTaxonomy


def _test_taxonomy() -> TopicTaxonomy:
    return TopicTaxonomy(
        version="test",
        roots=[
            TopicNode(
                id="mechanics",
                display_zh="力学",
                children=[
                    TopicNode(
                        id="celestial_mechanics",
                        display_zh="天体运动",
                        children=[
                            TopicNode(id="orbital_theory", display_zh="轨道理论"),
                        ],
                    ),
                    TopicNode(id="kinematics", display_zh="运动学"),
                ],
            ),
            TopicNode(
                id="thermodynamics",
                display_zh="热学",
                children=[
                    TopicNode(id="gas_laws", display_zh="气体定律"),
                ],
            ),
        ],
    )


def _provider_config(api_key: str = "sk-test") -> ResolvedProviderConfig:
    return ResolvedProviderConfig(
        name="openrouter",
        kind="openrouter",
        api_key=api_key,
        base_url="https://x.test",
    )


class FakeTopicProvider:
    """Returns a fixed TopicAssignmentOutput JSON."""

    def __init__(
        self,
        output: TopicAssignmentOutput | None = None,
        raw_content: str | None = None,
    ) -> None:
        self.output = output or TopicAssignmentOutput(
            topic_path="力学/天体运动/轨道理论",
            confidence=0.9,
            rationale="题目考查天体轨道运动",
        )
        self.raw_content = raw_content
        self.last_messages: list[dict[str, str]] | None = None

    def complete(
        self,
        messages: list[dict[str, str]],
        params: ModelParams,
        response_model: type[Any] | None = None,
    ) -> LLMResponse:
        self.last_messages = messages
        if self.raw_content is not None:
            return LLMResponse(content=self.raw_content, usage=LLMUsage())
        return LLMResponse(content=self.output.model_dump_json(), usage=LLMUsage())


def test_assign_topic_returns_valid_path() -> None:
    result = assign_topic(
        problem_id="p1",
        ocr_text="天体轨道运动问题",
        taxonomy=_test_taxonomy(),
        config=AppConfig(),
        provider_config=_provider_config(),
        llm_provider=FakeTopicProvider(),
    )
    assert result.topic_path == "力学/天体运动/轨道理论"
    assert result.confidence == 0.9


def test_assign_topic_rejects_invalid_path() -> None:
    fake = FakeTopicProvider(
        output=TopicAssignmentOutput(
            topic_path="力学/不存在的分类",
            confidence=0.5,
            rationale="编造的路径",
        )
    )
    with pytest.raises(IndexBuildError, match="invalid topic path"):
        assign_topic(
            problem_id="p1",
            ocr_text="test",
            taxonomy=_test_taxonomy(),
            config=AppConfig(),
            provider_config=_provider_config(),
            llm_provider=fake,
        )


def test_assign_topic_writes_trace(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.jsonl"
    assign_topic(
        problem_id="p1",
        ocr_text="test",
        taxonomy=_test_taxonomy(),
        config=AppConfig(),
        provider_config=_provider_config(),
        llm_provider=FakeTopicProvider(),
        trace_path=trace_path,
    )
    assert trace_path.exists()
    record = json.loads(trace_path.read_text(encoding="utf-8"))
    assert record["step_id"] == "topic_p1"
    assert record["status"] == "passed"


def test_assign_topic_trace_redacts_secret(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.jsonl"
    api_key = "sk-secret-key-123"
    fake = FakeTopicProvider(
        output=TopicAssignmentOutput(
            topic_path="力学/不存在的分类",
            confidence=0.5,
            rationale="编造的路径",
        )
    )
    with pytest.raises(IndexBuildError):
        assign_topic(
            problem_id="p1",
            ocr_text="test",
            taxonomy=_test_taxonomy(),
            config=AppConfig(),
            provider_config=_provider_config(api_key),
            llm_provider=fake,
            trace_path=trace_path,
        )
    text = trace_path.read_text(encoding="utf-8")
    assert api_key not in text


def test_assign_topic_validation_error() -> None:
    fake = FakeTopicProvider(raw_content='{"bad": "json"}')
    with pytest.raises(IndexBuildError, match="validation"):
        assign_topic(
            problem_id="p1",
            ocr_text="test",
            taxonomy=_test_taxonomy(),
            config=AppConfig(),
            provider_config=_provider_config(),
            llm_provider=fake,
        )


def test_topic_prompt_contains_valid_paths() -> None:
    taxonomy = _test_taxonomy()
    rendered = _render_topic_prompt("p1", "天体运动题目", taxonomy)
    assert "力学/天体运动/轨道理论" in rendered
    assert "热学/气体定律" in rendered
    assert "p1" in rendered


def test_manifest_includes_topic_assignment() -> None:
    manifest_path = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "cpho_cli"
        / "core"
        / "index"
        / "prompts"
        / "MANIFEST.yml"
    )
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert "topic_assignment" in data["templates"]
