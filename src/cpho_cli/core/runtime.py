from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from graphlib import CycleError, TopologicalSorter
from pathlib import Path
from typing import Any

from cpho_cli.models.runtime import CheckpointRecord, ResumeState, SkillRunResult, TraceRecord
from cpho_cli.models.skills import SkillSpec, SkillStep

StepHandler = Callable[[SkillStep, Mapping[str, Any]], Mapping[str, Any]]


class SkillRuntimeError(RuntimeError):
    """Raised when skill execution cannot continue."""


def redact_secrets(value: str, secrets: list[str]) -> str:
    redacted = value
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


class SkillRuntime:
    def __init__(
        self,
        handlers: Mapping[str, StepHandler],
        trace_path: Path | None = None,
        checkpoint_dir: Path | None = None,
        secrets: list[str] | None = None,
    ) -> None:
        self.handlers = handlers
        self.trace_path = trace_path
        self.checkpoint_dir = checkpoint_dir
        self.secrets = secrets or []

    def _order(self, spec: SkillSpec) -> list[SkillStep]:
        producers: dict[str, str] = {}
        graph: dict[str, set[str]] = {}
        steps_by_id = {step.id: step for step in spec.steps}
        for step in spec.steps:
            graph.setdefault(step.id, set(step.depends_on))
            for key in step.input_keys:
                if key in producers:
                    graph[step.id].add(producers[key])
            for key in step.output_keys:
                if key in producers:
                    raise SkillRuntimeError(f"Duplicate output key: {key}")
                producers[key] = step.id
        try:
            return [steps_by_id[step_id] for step_id in TopologicalSorter(graph).static_order()]
        except CycleError as exc:
            raise SkillRuntimeError("Skill DAG contains a cycle.") from exc

    def _write_trace(self, record: TraceRecord) -> None:
        if self.trace_path is None:
            return
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        text = record.model_dump_json()
        text = redact_secrets(text, self.secrets)
        with self.trace_path.open("a", encoding="utf-8") as handle:
            handle.write(text + "\n")

    def _write_checkpoint(self, record: CheckpointRecord) -> None:
        if self.checkpoint_dir is None:
            return
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        path = self.checkpoint_dir / f"{record.failed_step_id}.checkpoint.json"
        path.write_text(record.model_dump_json(indent=2), encoding="utf-8")

    def run(self, spec: SkillSpec, initial_blackboard: Mapping[str, Any]) -> SkillRunResult:
        blackboard: dict[str, Any] = dict(initial_blackboard)
        statuses: dict[str, str] = {}
        for step in self._order(spec):
            missing = [key for key in step.input_keys if key not in blackboard]
            if missing:
                raise SkillRuntimeError(f"Step {step.id} missing input keys: {missing}")
            handler = self.handlers.get(step.kind)
            if handler is None:
                raise SkillRuntimeError(f"No handler registered for step kind: {step.kind}")
            started = datetime.now(timezone.utc)
            try:
                values = {key: blackboard[key] for key in step.input_keys}
                outputs = dict(handler(step, values))
                missing_outputs = [key for key in step.output_keys if key not in outputs]
                if missing_outputs:
                    raise SkillRuntimeError(
                        f"Step {step.id} missing output keys: {missing_outputs}"
                    )
                blackboard.update(outputs)
                statuses[step.id] = "passed"
                self._write_trace(
                    TraceRecord(
                        step_id=step.id,
                        status="passed",
                        input_keys=step.input_keys,
                        output_keys=step.output_keys,
                        started_at=started,
                        finished_at=datetime.now(timezone.utc),
                    )
                )
            except Exception as exc:
                statuses[step.id] = "failed"
                self._write_trace(
                    TraceRecord(
                        step_id=step.id,
                        status="failed",
                        input_keys=step.input_keys,
                        output_keys=step.output_keys,
                        started_at=started,
                        finished_at=datetime.now(timezone.utc),
                        error=redact_secrets(str(exc), self.secrets),
                    )
                )
                self._write_checkpoint(
                    CheckpointRecord(
                        failed_step_id=step.id,
                        blackboard_keys=sorted(blackboard),
                        error=redact_secrets(str(exc), self.secrets),
                    )
                )
                raise
        return SkillRunResult(blackboard=blackboard, step_statuses=statuses)


def load_resume_state(checkpoint_path: Path) -> ResumeState:
    data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    return ResumeState.model_validate(data)

