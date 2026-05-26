from __future__ import annotations

import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, TextIO

from cpho_cli.core.runtime import StepHandler
from cpho_cli.models.skills import SkillStep


@dataclass(frozen=True)
class ProgressEvent:
    step_id: str
    status: str
    activity: str
    elapsed_seconds: float = 0.0
    error: str | None = None


class ProgressReporter(Protocol):
    def emit(self, event: ProgressEvent) -> None:
        """Emit one progress event."""


class PlainProgressReporter:
    def __init__(self, stream: TextIO | None = None) -> None:
        self.stream = stream or sys.stdout

    def emit(self, event: ProgressEvent) -> None:
        detail = (
            f"{event.status}: {event.step_id} - {event.activity} "
            f"elapsed={event.elapsed_seconds:.2f}s"
        )
        if event.error:
            detail += f" error={event.error}"
        print(detail, file=self.stream)


class RichProgressReporter:
    def __init__(self, stream: TextIO | None = None) -> None:
        self.stream = stream or sys.stdout
        self._plain = PlainProgressReporter(stream=self.stream)

    def emit(self, event: ProgressEvent) -> None:
        if not self.stream.isatty():
            self._plain.emit(event)
            return
        from rich.console import Console
        from rich.spinner import Spinner

        console = Console(file=self.stream)
        spinner = Spinner("dots", text=f"{event.step_id} - {event.activity}")
        console.print(spinner)


def wrap_handlers(
    handlers: Mapping[str, StepHandler],
    reporter: ProgressReporter,
) -> dict[str, StepHandler]:
    wrapped: dict[str, StepHandler] = {}
    for kind, handler in handlers.items():
        wrapped[kind] = _wrap_handler(handler, reporter)
    return wrapped


def _wrap_handler(handler: StepHandler, reporter: ProgressReporter) -> StepHandler:
    def wrapped(step: SkillStep, values: Mapping[str, Any]) -> Mapping[str, Any]:
        activity = step.prompt_template or step.kind
        started = time.monotonic()
        reporter.emit(ProgressEvent(step_id=step.id, status="start", activity=activity))
        try:
            result = handler(step, values)
        except Exception as exc:
            reporter.emit(
                ProgressEvent(
                    step_id=step.id,
                    status="error",
                    activity=activity,
                    elapsed_seconds=time.monotonic() - started,
                    error=str(exc),
                )
            )
            raise
        reporter.emit(
            ProgressEvent(
                step_id=step.id,
                status="done",
                activity=activity,
                elapsed_seconds=time.monotonic() - started,
            )
        )
        return result

    return wrapped


__all__ = [
    "PlainProgressReporter",
    "ProgressEvent",
    "ProgressReporter",
    "RichProgressReporter",
    "wrap_handlers",
]
