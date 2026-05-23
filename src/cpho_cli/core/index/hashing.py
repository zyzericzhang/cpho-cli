from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

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

IndexAction = Literal["full_index", "re_ocr_and_re_tag", "re_tag_only", "refinement_only", "skip"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_json(obj: object) -> str:
    text = json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compose_file_fingerprint(problem_path: Path, answer_path: Path | None) -> FileFingerprint:
    # D-14: mtime is informational only; sha256 is the authoritative cache trigger.
    problem_stat = problem_path.stat()
    answer_sha256 = None
    answer_size_bytes = None
    if answer_path is not None and answer_path.exists():
        answer_sha256 = sha256_file(answer_path)
        answer_size_bytes = answer_path.stat().st_size

    return FileFingerprint(
        problem_sha256=sha256_file(problem_path),
        answer_sha256=answer_sha256,
        problem_size_bytes=problem_stat.st_size,
        answer_size_bytes=answer_size_bytes,
        problem_mtime_ns=problem_stat.st_mtime_ns,
    )


def compose_semantic_fingerprint(
    file_fp: FileFingerprint,
    ocr_engine: str,
    ocr_engine_version: str,
    ocr_config: dict[str, object],
    tag_prompt_version: str,
    tag_schema_version: str,
    model_name: str,
    model_temperature: float,
    vocabulary_version: str,
) -> SemanticFingerprint:
    return SemanticFingerprint(
        file_fp_hash=file_fp.problem_sha256[:16],
        ocr_engine=ocr_engine,
        ocr_engine_version=ocr_engine_version,
        ocr_config_hash=sha256_json(ocr_config),
        tag_prompt_version=tag_prompt_version,
        tag_schema_version=tag_schema_version,
        model_name=model_name,
        model_temperature=model_temperature,
        vocabulary_version=vocabulary_version,
    )


def compose_user_learning_fingerprint(notebook: UserNotebookEntry | None) -> UserLearningFingerprint:
    if notebook is None:
        return UserLearningFingerprint()

    notes_sha256 = sha256_json(
        {
            "key_points": notebook.key_points,
            "stuck_points": notebook.stuck_points,
            "free_text_notes": notebook.free_text_notes,
        }
    )
    user_tags_sha256 = sha256_json({"user_tags": notebook.user_tags})
    # Phase 3 will populate QA history independently of Phase 2 notebook hashing.
    return UserLearningFingerprint(
        notes_sha256=notes_sha256,
        user_tags_sha256=user_tags_sha256,
        qa_history_sha256=None,
    )


def compose_index_fingerprint(
    file_fp: FileFingerprint,
    semantic_fp: SemanticFingerprint,
    user_learning_fp: UserLearningFingerprint,
) -> IndexFingerprint:
    return IndexFingerprint(file=file_fp, semantic=semantic_fp, user_learning=user_learning_fp)


# D-14 dispatcher. Order matters: file > semantic > user_learning. File changes invalidate
# everything below; semantic changes keep OCR cache; user_learning changes touch neither OCR
# nor LLM (refinement-only pass).
def decide_action(old: IndexEntry | None, new_fp: IndexFingerprint) -> IndexAction:
    if old is None:
        return "full_index"
    if old.fingerprint.file != new_fp.file:
        return "re_ocr_and_re_tag"
    if old.fingerprint.semantic != new_fp.semantic:
        return "re_tag_only"
    if old.fingerprint.user_learning != new_fp.user_learning:
        return "refinement_only"
    return "skip"
