from __future__ import annotations

from pydantic import ConfigDict, Field, model_validator

from cpho_cli.models.config import StrictModel


class SlotSpec(StrictModel):
    topic: str | None = None
    tags: list[str] = Field(default_factory=list)
    requirement: str | None = None


class CompositionSlot(StrictModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    problem_id: str | None = None
    pass_slot: bool = Field(False, alias="pass")
    spec: SlotSpec | None = None

    @model_validator(mode="after")
    def validate_single_mode(self) -> "CompositionSlot":
        mode_count = sum(
            [
                self.problem_id is not None,
                self.pass_slot,
                self.spec is not None,
            ]
        )
        if mode_count != 1:
            raise ValueError("slot 必须在 problem_id / pass / spec 中三选一")
        return self


class CompositionFile(StrictModel):
    name: str
    slots: dict[int, CompositionSlot]


__all__ = ["CompositionFile", "CompositionSlot", "SlotSpec"]
