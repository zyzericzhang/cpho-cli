from __future__ import annotations

import json
from pathlib import Path

from cpho_cli.core.input_routing import choose_input_route
from cpho_cli.core.skill_handlers import make_llm_handler
from cpho_cli.models.config import ModelParams
from cpho_cli.models.llm import LLMResponse, ModelCapabilities
from cpho_cli.models.skills import SkillStep


class FakeProvider:
    def __init__(self, capabilities: ModelCapabilities) -> None:
        self.capabilities = capabilities
        self.last_content = None

    def complete(self, messages, params, response_model=None):  # type: ignore[no-untyped-def]
        self.last_content = messages[-1]["content"]
        return LLMResponse(content=json.dumps({"answer": "ok"}))

    def stream(self, messages, params):  # type: ignore[no-untyped-def]
        yield ""


def test_choose_input_route_prefers_pdf_when_supported() -> None:
    route = choose_input_route(
        [Path("problem.pdf")],
        ModelCapabilities(input_modalities={"text", "file"}),
    )

    assert route.input_modality_used == "multimodal_pdf"
    assert route.file_paths == [Path("problem.pdf")]


def test_choose_input_route_uses_image_when_supported() -> None:
    route = choose_input_route(
        [Path("problem.png")],
        ModelCapabilities(input_modalities={"text", "image"}),
    )

    assert route.input_modality_used == "multimodal_image"


def test_choose_input_route_falls_back_to_ocr_text() -> None:
    route = choose_input_route(
        [Path("problem.pdf")],
        ModelCapabilities(input_modalities={"text"}),
    )

    assert route.input_modality_used == "ocr_text"
    assert route.file_paths == []
    assert route.warning is not None


def test_llm_handler_exposes_input_route_outputs(tmp_path: Path) -> None:
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    (prompts / "p.md.j2").write_text("{{ problem_text }}", encoding="utf-8")
    problem = tmp_path / "problem.pdf"
    problem.write_bytes(b"%PDF-1.4")
    provider = FakeProvider(ModelCapabilities(input_modalities={"text"}))
    handler = make_llm_handler(provider, ModelParams(name="fake"), tmp_path)

    result = handler(
        SkillStep(
            id="route",
            kind="llm",
            input_keys=["problem_text", "problem_file"],
            output_keys=["answer", "input_modality_used", "input_routing_warning"],
            prompt_template="p.md.j2",
            requires_multimodal=True,
        ),
        {"problem_text": "ocr text", "problem_file": problem},
    )

    assert result["answer"] == "ok"
    assert result["input_modality_used"] == "ocr_text"
    assert "降级" in result["input_routing_warning"]
    assert provider.last_content == "ocr text"
