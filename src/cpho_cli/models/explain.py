from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field

from cpho_cli.models.config import StrictModel


class ExplainPanel(str, Enum):
    APPROACH = "approach"
    ANSWER_REPLACEMENT = "answer_replacement"
    ALTERNATIVE_METHODS = "alternative_methods"

    @property
    def display_zh(self) -> str:
        return {
            ExplainPanel.APPROACH: "思路描述",
            ExplainPanel.ANSWER_REPLACEMENT: "标答替换",
            ExplainPanel.ALTERNATIVE_METHODS: "其他方法",
        }[self]


class ExplainStreamChunk(StrictModel):
    panel: ExplainPanel
    text: str
    stage: str


class PanelExplainOutput(StrictModel):
    panel: ExplainPanel
    markdown: str


class ExplainProvenance(StrictModel):
    input_modality_used: str = "ocr_text"
    knowledge_sources: list[str] = Field(default_factory=list)


class ExplainResult(StrictModel):
    problem_name: str
    panel_outputs: list[PanelExplainOutput]
    candidate_tags: list[str] = Field(default_factory=list)
    markdown_path: Path
    provenance: ExplainProvenance = Field(default_factory=ExplainProvenance)


__all__ = [
    "ExplainPanel",
    "ExplainProvenance",
    "ExplainResult",
    "ExplainStreamChunk",
    "PanelExplainOutput",
]
