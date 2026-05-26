"""Tests for topic assignment integration in build_index."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from cpho_cli.core.index import IndexBuildError, VocabularyError
from cpho_cli.core.index.builder import build_index
from cpho_cli.core.index.storage import load_index
from cpho_cli.core.index.tagging import TagRefinementOutput
from cpho_cli.core.index.topic_assignment import TopicAssignmentOutput
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import LLMResponse, LLMUsage, ModelCapabilities

from conftest import FakeOCRProvider, setup_workspace


class FakeLLMProviderWithTopic:
    """Returns TagRefinementOutput or TopicAssignmentOutput based on response_model."""

    def __init__(
        self,
        tag_output: TagRefinementOutput | None = None,
        topic_output: TopicAssignmentOutput | None = None,
    ) -> None:
        self.tag_output = tag_output or TagRefinementOutput(
            selected_physics_models=["energy_conservation"],
            selected_math_techniques=["dimensional_analysis"],
            selected_heuristics=["free_body_diagram"],
            difficulty_aspects=["受力分析"],
        )
        self.topic_output = topic_output or TopicAssignmentOutput(
            topic_path="力学/天体运动/轨道理论",
            confidence=0.9,
            rationale="考查天体轨道",
        )
        self.calls: list[dict[str, Any]] = []

    def complete(
        self,
        messages: list[dict[str, Any]],
        params: ModelParams,
        response_model: type[Any] | None = None,
    ) -> LLMResponse:
        self.calls.append(
            {"messages": messages, "params": params, "response_model": response_model}
        )
        if response_model is not None and response_model.__name__ == "TopicAssignmentOutput":
            return LLMResponse(
                content=self.topic_output.model_dump_json(),
                usage=LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
                raw={},
            )
        return LLMResponse(
            content=self.tag_output.model_dump_json(),
            usage=LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
            raw={},
        )


def _patch_rapidocr_version(monkeypatch: pytest.MonkeyPatch, version: str = "3.0.0") -> None:
    monkeypatch.setattr("cpho_cli.core.index.builder._rapidocr_version", lambda: version)


def test_build_index_assigns_topic_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProviderWithTopic(),
        ocr_strategy="reuse",
    )
    entries = load_index(ws)
    assert len(entries) == 1
    assert entries[0].topic_path == "力学/天体运动/轨道理论"


def test_build_index_topic_default_uses_text_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    llm = FakeLLMProviderWithTopic()

    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=llm,
        ocr_strategy="reuse",
    )

    topic_calls = [
        call
        for call in llm.calls
        if call["response_model"] is not None
        and call["response_model"].__name__ == "TopicAssignmentOutput"
    ]
    assert topic_calls
    assert isinstance(topic_calls[0]["messages"][1]["content"], str)


def test_build_index_topic_vision_receives_image_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    llm = FakeLLMProviderWithTopic()
    llm.capabilities = ModelCapabilities(input_modalities={"text", "image"})

    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=llm,
        ocr_strategy="reuse",
        vision=True,
    )

    topic_calls = [
        call
        for call in llm.calls
        if call["response_model"] is not None
        and call["response_model"].__name__ == "TopicAssignmentOutput"
    ]
    assert topic_calls
    content = topic_calls[0]["messages"][1]["content"]
    assert isinstance(content, list)
    assert any(block["type"] == "image_url" for block in content)


def test_build_index_topic_preserved_on_skip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    llm = FakeLLMProviderWithTopic()
    kwargs = dict(
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=llm,
        ocr_strategy="reuse",
    )
    build_index(ws, **kwargs)
    entries1 = load_index(ws)
    assert entries1[0].topic_path == "力学/天体运动/轨道理论"

    # Second run: fingerprint matches, should skip => preserve topic_path
    initial_calls = len(llm.calls)
    build_index(ws, **kwargs)
    entries2 = load_index(ws)
    assert entries2[0].topic_path == "力学/天体运动/轨道理论"
    # No new LLM calls for the skipped entry
    assert len(llm.calls) == initial_calls


def test_build_index_topic_failure_non_blocking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])

    monkeypatch.setattr(
        "cpho_cli.core.index.builder.assign_topic",
        lambda *a, **kw: (_ for _ in ()).throw(IndexBuildError("topic fail")),
    )

    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProviderWithTopic(),
        ocr_strategy="reuse",
    )
    entries = load_index(ws)
    assert len(entries) == 1
    # topic_path is None because assignment failed, but tags are still present
    assert entries[0].topic_path is None
    assert len(entries[0].physics_model_tags) > 0


def test_build_index_topic_vision_failure_non_blocking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])
    llm = FakeLLMProviderWithTopic()
    llm.capabilities = ModelCapabilities(input_modalities={"text", "image"})

    monkeypatch.setattr(
        "cpho_cli.core.index.builder.assign_topic",
        lambda *a, **kw: (_ for _ in ()).throw(IndexBuildError("topic fail")),
    )

    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=llm,
        ocr_strategy="reuse",
        vision=True,
    )
    entries = load_index(ws)
    assert len(entries) == 1
    assert entries[0].topic_path is None
    assert len(entries[0].physics_model_tags) > 0


def test_build_index_no_topic_taxonomy_continues(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_rapidocr_version(monkeypatch)
    ws = setup_workspace(tmp_path, problem_names=["p1"])

    monkeypatch.setattr(
        "cpho_cli.core.index.builder.load_merged_topic_taxonomy",
        lambda *a, **kw: (_ for _ in ()).throw(VocabularyError("taxonomy fail")),
    )

    build_index(
        ws,
        config_path=ws / "config.local.yml",
        ocr_provider=FakeOCRProvider(),
        llm_provider=FakeLLMProviderWithTopic(),
        ocr_strategy="reuse",
    )
    entries = load_index(ws)
    assert len(entries) == 1
    assert entries[0].topic_path is None
