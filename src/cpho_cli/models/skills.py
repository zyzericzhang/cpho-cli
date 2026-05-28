from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class PipelineStepDescription(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: str
    description: str | None = None
    default_model: str | None = None
    requires_multimodal: bool = False
    prompt_template: str | None = None
    prompt_path: Path | None = None
    input_keys: list[str] = Field(default_factory=list)
    output_keys: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)


class PipelineEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    target: str
    reason: str


class PipelineDescription(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    steps: list[PipelineStepDescription] = Field(default_factory=list)
    edges: list[PipelineEdge] = Field(default_factory=list)


class SkillStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    kind: str
    description: str | None = None
    default_model: str | None = None
    requires_multimodal: bool = False
    input_keys: list[str] = Field(default_factory=list)
    output_keys: list[str] = Field(default_factory=list)
    prompt_template: str | None = None
    depends_on: list[str] = Field(default_factory=list)


class SkillSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    steps: list[SkillStep] = Field(default_factory=list)

    def describe(self, skill_root: Path | None = None) -> PipelineDescription:
        producers: dict[str, str] = {}
        for step in self.steps:
            for key in step.output_keys:
                producers.setdefault(key, step.id)

        edges: list[PipelineEdge] = []
        seen_edges: set[tuple[str, str, str]] = set()
        step_ids = {step.id for step in self.steps}
        for step in self.steps:
            for dependency in step.depends_on:
                if dependency not in step_ids:
                    continue
                edge = (dependency, step.id, "depends_on")
                if edge not in seen_edges:
                    edges.append(PipelineEdge(source=edge[0], target=edge[1], reason=edge[2]))
                    seen_edges.add(edge)
            for key in step.input_keys:
                producer = producers.get(key)
                if producer is None or producer == step.id:
                    continue
                edge = (producer, step.id, f"input:{key}")
                if edge not in seen_edges:
                    edges.append(PipelineEdge(source=edge[0], target=edge[1], reason=edge[2]))
                    seen_edges.add(edge)

        descriptions = [
            PipelineStepDescription(
                id=step.id,
                kind=step.kind,
                description=step.description,
                default_model=step.default_model,
                requires_multimodal=step.requires_multimodal,
                prompt_template=step.prompt_template,
                prompt_path=(
                    skill_root / "prompts" / step.prompt_template
                    if skill_root is not None and step.prompt_template is not None
                    else None
                ),
                input_keys=step.input_keys,
                output_keys=step.output_keys,
                depends_on=step.depends_on,
            )
            for step in self.steps
        ]
        return PipelineDescription(
            name=self.name,
            inputs=self.inputs,
            outputs=self.outputs,
            steps=descriptions,
            edges=edges,
        )


SkillPipeline = SkillSpec
