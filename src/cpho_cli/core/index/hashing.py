from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from cpho_cli.models.index import (
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    UserLearningFingerprint,
    UserNotebookEntry,
)

# Increment when IndexEntry / TaggedReference / IndexFingerprint schemas change. Embedded in SemanticFingerprint per D-14.
TAG_SCHEMA_VERSION = "v1"

_IMPORTS_USED_BY_LATER_TASKS = (
    datetime,
    FileFingerprint,
    IndexEntry,
    IndexFingerprint,
    SemanticFingerprint,
    UserLearningFingerprint,
    UserNotebookEntry,
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_json(obj: object) -> str:
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
