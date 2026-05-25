"""build_index orchestrator: discover -> fingerprint -> decide -> OCR -> tag -> topic -> write."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

import yaml

from cpho_cli.core.config import load_config, resolve_model_params, resolve_provider_config
from cpho_cli.core.documents import load_document
from cpho_cli.core.index import IndexBuildError
from cpho_cli.core.index.hashing import (
    TAG_SCHEMA_VERSION,
    compose_file_fingerprint,
    compose_index_fingerprint,
    compose_semantic_fingerprint,
    compose_user_learning_fingerprint,
    decide_action,
)
from cpho_cli.core.index.notebook import get_problem_notes
from cpho_cli.core.index.ocr_cache import (
    OCR_CACHE_DIRNAME,
    RAPIDOCR_ENGINE_NAME,
    CachedOCRProvider,
    OcrUpgradeDecisionRequired,
    _rapidocr_version,
    detect_ocr_engine_upgrade,
    ocr_config_hash,
)
from cpho_cli.core.index.storage import load_existing_index_for_rebuild, write_index
from cpho_cli.core.index.tagging import CanonicalMappingResult, load_tag_prompt_version, refine_tags
from cpho_cli.core.index.topic_assignment import assign_topic
from cpho_cli.core.index.topic_vocabulary import load_merged_topic_taxonomy
from cpho_cli.core.index.vocabulary import (
    list_pending_candidates,
    load_merged_vocabulary,
    normalize_alias,
)
from cpho_cli.core.llm import LLMProvider, create_llm_provider
from cpho_cli.core.ocr import OCRProvider, RapidOCRProvider
from cpho_cli.core.splitting import split_paper
from cpho_cli.core.splitting.llm import load_split_prompt_version
from cpho_cli.core.workspace import discover_workspace
from cpho_cli.models.config import ResolvedProviderConfig
from cpho_cli.models.documents import PaperFile, SplitMethod
from cpho_cli.models.index import (
    CandidateTag,
    IndexEntry,
    IndexRunStats,
    UserNotebookEntry,
)


class IndexProgress(TypedDict, total=False):
    """Progress event emitted by build_index at key milestones."""
    phase: str
    file_path: str
    file_index: int
    total_files: int
    problem_id: str
    problems_extracted_so_far: int
    problems_processed_so_far: int
    physics_count: int
    math_count: int
    heuristic_count: int
    topic_path: str


def _ocr_config() -> dict[str, object]:
    return {"low_confidence_threshold": 0.6}


def _ensure_llm_provider(
    existing: LLMProvider | None,
    provider_config: ResolvedProviderConfig,
) -> LLMProvider:
    if existing is not None:
        return existing
    return create_llm_provider(
        kind=provider_config.kind,
        api_key=provider_config.api_key,
        base_url=provider_config.base_url,
        timeout=provider_config.timeout,
    )


def _merge_candidates(workspace_root: Path, new_candidates: list[CandidateTag]) -> int:
    """Merge new candidates into pending.yml; returns count of NEW (not seen before) candidates."""
    pending_path = workspace_root / ".cpho" / "vocabulary" / "pending.yml"
    existing: list[CandidateTag] = []
    if pending_path.exists():
        raw = yaml.safe_load(pending_path.read_text(encoding="utf-8")) or []
        if isinstance(raw, list):
            existing = [CandidateTag.model_validate(item) for item in raw]

    by_key: dict[str, CandidateTag] = {}
    for c in existing:
        key = normalize_alias(c.display_zh_suggestion)
        by_key[key] = c

    new_count = 0
    for c in new_candidates:
        key = normalize_alias(c.display_zh_suggestion)
        if key in by_key:
            old = by_key[key]
            by_key[key] = old.model_copy(update={"occurrences": old.occurrences + 1})
        else:
            by_key[key] = c
            new_count += 1

    pending_path.parent.mkdir(parents=True, exist_ok=True)
    data = [c.model_dump(mode="json") for c in by_key.values()]
    tmp = pending_path.with_suffix(pending_path.suffix + ".tmp")
    tmp.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    tmp.replace(pending_path)
    return new_count


def build_index(
    workspace_root: Path,
    config_path: Path | None = None,
    provider_name: str | None = None,
    *,
    force: bool = False,
    force_all: bool = False,
    only_new: bool = False,
    dry_run: bool = False,
    ocr_strategy: str = "prompt",
    ocr_provider: OCRProvider | None = None,
    llm_provider: LLMProvider | None = None,
    target_subpath: Path | None = None,
    on_progress: Callable[[IndexProgress], None] | None = None,
) -> IndexRunStats:
    """Orchestrate workspace indexing.

    When both ``--force`` and ``--only-new`` are set, ``--force`` wins for
    entries that already exist (force is explicit user intent).

    If *target_subpath* is given, only that subdirectory (relative to
    *workspace_root*) is scanned for papers.
    """
    workspace_root = workspace_root.resolve()
    if force_all:
        force = True
    discovery_root = workspace_root
    if target_subpath is not None:
        discovery_root = (workspace_root / target_subpath).resolve()
        if not discovery_root.is_relative_to(workspace_root):
            raise ValueError(f"target_subpath must be under workspace_root: {target_subpath}")
    discovery = discover_workspace(discovery_root)

    # Build paper inputs: pairs + unmatched papers, skip ambiguous.
    papers: list[tuple[PaperFile, PaperFile | None]] = []
    for pair in discovery.pairs:
        papers.append((pair.paper, pair.answer))
    for unmatched in discovery.unmatched_problems:
        papers.append((unmatched, None))

    stats = IndexRunStats()

    if on_progress is not None:
        on_progress(IndexProgress(phase="begin", total_files=len(papers)))

    if dry_run:
        load_merged_vocabulary(workspace_root)
        stats.total_problems = len(papers)
        return stats

    config = load_config(config_path)
    provider_config = resolve_provider_config(config, os.environ, provider_name)
    active_llm_provider = _ensure_llm_provider(llm_provider, provider_config)
    vocabulary = load_merged_vocabulary(workspace_root)

    # Load topic taxonomy (non-blocking: failure disables topic assignment)
    topic_taxonomy = None
    try:
        topic_taxonomy = load_merged_topic_taxonomy(workspace_root)
    except Exception:
        logging.getLogger(__name__).warning(
            "Topic taxonomy failed to load; topic assignment disabled for this run."
        )

    ocr_engine_version = _rapidocr_version()
    oc_hash = ocr_config_hash(_ocr_config())

    # OCR strategy handling
    if ocr_strategy == "prompt":
        delta = detect_ocr_engine_upgrade(
            workspace_root, RAPIDOCR_ENGINE_NAME, ocr_engine_version, oc_hash
        )
        if delta is not None:
            raise OcrUpgradeDecisionRequired(delta)
    elif ocr_strategy == "reuse":
        stats.ocr_engine_upgrade_detected = False
    elif ocr_strategy == "rebuild":
        stats.ocr_engine_upgrade_detected = True
    elif ocr_strategy == "new-only":
        stats.ocr_engine_upgrade_detected = True
        only_new = True

    tag_prompt_version = load_tag_prompt_version()
    split_prompt_version = load_split_prompt_version()
    params = resolve_model_params(config, "index", provider_name=provider_name)

    index_path = workspace_root / ".cpho" / "index.jsonl"
    existing_entries: dict[str, IndexEntry] = {}
    if index_path.exists():
        load_result = load_existing_index_for_rebuild(workspace_root, TAG_SCHEMA_VERSION)
        existing_entries = {e.problem_id: e for e in load_result.entries}

    inner_ocr = ocr_provider or RapidOCRProvider()
    cached_ocr = CachedOCRProvider(
        inner_ocr,
        workspace_root / OCR_CACHE_DIRNAME,
        RAPIDOCR_ENGINE_NAME,
        ocr_engine_version,
    )

    result_entries: dict[str, IndexEntry] = dict(existing_entries)
    trace_path = workspace_root / ".cpho" / "run-trace.jsonl"
    all_candidates: list[CandidateTag] = []

    for file_idx, (paper_file, answer_file) in enumerate(papers, start=1):
        answer_path = answer_file.path if answer_file else None
        file_fp = compose_file_fingerprint(paper_file.path, answer_path)

        paper_document = load_document(paper_file.path)
        paper_ocr = cached_ocr.extract(paper_document)
        answer_ocr = None
        if answer_file is not None:
            answer_document = load_document(answer_file.path)
            answer_ocr = cached_ocr.extract(answer_document)

        if on_progress is not None:
            on_progress(IndexProgress(
                phase="paper_split_start",
                file_path=str(paper_file.path),
                file_index=file_idx,
                total_files=len(papers),
            ))

        try:
            split_outcome = split_paper(
                paper_ocr,
                answer_ocr,
                paper_file=paper_file,
                answer_file=answer_file,
                paper_sha256=file_fp.problem_sha256,
                llm_provider=active_llm_provider,
                llm_params=params,
            )
        except Exception as exc:
            raise IndexBuildError(f"试卷切分失败: {paper_file.path}: {exc}") from exc
        stats.papers_split += 1
        stats.problems_extracted += len(split_outcome.problems)
        stats.total_problems += len(split_outcome.problems)

        if on_progress is not None:
            on_progress(IndexProgress(
                phase="paper_split_done",
                file_index=file_idx,
                total_files=len(papers),
                problems_extracted_so_far=stats.problems_extracted,
            ))

        for problem_entry in split_outcome.problems:
            if problem_entry.split_method is SplitMethod.RULES:
                stats.split_method_rules += 1
            elif problem_entry.split_method is SplitMethod.LLM:
                stats.split_method_llm += 1
            elif problem_entry.split_method is SplitMethod.SINGLE:
                stats.split_method_single += 1

        for problem_entry in split_outcome.problems:
            problem_id = problem_entry.problem_id

            notebook: UserNotebookEntry | None = get_problem_notes(workspace_root, problem_id)
            user_learning_fp = compose_user_learning_fingerprint(notebook)

            semantic_fp = compose_semantic_fingerprint(
                file_fp=file_fp,
                ocr_engine=RAPIDOCR_ENGINE_NAME,
                ocr_engine_version=ocr_engine_version,
                ocr_config=_ocr_config(),
                tag_prompt_version=tag_prompt_version,
                split_prompt_version=split_prompt_version,
                tag_schema_version=TAG_SCHEMA_VERSION,
                model_name=params.name or "",
                model_temperature=params.temperature if params.temperature is not None else 0.0,
                vocabulary_version=vocabulary.version,
            )
            fingerprint = compose_index_fingerprint(file_fp, semantic_fp, user_learning_fp)

            old = existing_entries.get(problem_id)
            action = decide_action(old, fingerprint)
            forced_override = False

            # only_new: skip existing (but force wins if both set)
            if only_new and old is not None and not force:
                action = "skip"

            # force overrides
            if force and old is not None:
                if action == "skip":
                    forced_override = True
                action = "re_ocr_and_re_tag"
            elif force and old is None:
                action = "full_index"

            # OCR rebuild strategy
            if (
                ocr_strategy == "rebuild"
                and old is not None
                and old.fingerprint.semantic.ocr_engine_version != ocr_engine_version
            ):
                action = "re_ocr_and_re_tag"

            # Dispatch
            if action == "skip":
                stats.tags_skipped += 1
                stats.file_unchanged += 1
                if on_progress is not None:
                    on_progress(IndexProgress(
                        phase="problem_skip",
                        problem_id=problem_id,
                        problems_processed_so_far=stats.tags_skipped + stats.tags_regenerated + stats.refinement_only,
                    ))
                continue

            if action == "refinement_only":
                entry = old.model_copy(  # type: ignore[union-attr]
                    update={
                        "fingerprint": fingerprint,
                        "user_confirmed_key_points": notebook.key_points if notebook else [],
                        "user_confirmed_stuck_points": notebook.stuck_points if notebook else [],
                        "indexed_at": datetime.now(timezone.utc),
                    }
                )
                stats.refinement_only += 1
                result_entries[problem_id] = entry
                continue

            # re_tag_only, re_ocr_and_re_tag, full_index all need tagging.
            ocr_text = problem_entry.problem_text

            if on_progress is not None:
                on_progress(IndexProgress(
                    phase="problem_tag_start",
                    problem_id=problem_id,
                    problems_processed_so_far=stats.tags_skipped + stats.tags_regenerated + stats.refinement_only,
                ))

            mapping: CanonicalMappingResult = refine_tags(
                problem_id,
                ocr_text,
                vocabulary,
                config,
                provider_config,
                llm_provider=active_llm_provider,
                trace_path=trace_path,
            )

            all_candidates.extend(mapping.candidates)

            # Topic assignment (non-blocking: failure sets topic_path to None)
            topic_path: str | None = None
            if topic_taxonomy is not None:
                try:
                    topic_result = assign_topic(
                        problem_id,
                        ocr_text,
                        topic_taxonomy,
                        config,
                        provider_config,
                        llm_provider=active_llm_provider,
                        trace_path=trace_path,
                    )
                    topic_path = topic_result.topic_path
                except Exception:
                    logging.getLogger(__name__).warning(
                        "Topic assignment failed for %s; continuing without topic.", problem_id
                    )

            entry = IndexEntry(
                problem_id=problem_id,
                problem_path=problem_entry.paper_path.relative_to(workspace_root),
                problem_page_range=problem_entry.problem_page_range,
                answer_path=(
                    problem_entry.answer_paper_path.relative_to(workspace_root)
                    if problem_entry.answer_paper_path
                    else None
                ),
                indexed_at=datetime.now(timezone.utc),
                physics_model_tags=mapping.physics_model_tags,
                math_technique_tags=mapping.math_technique_tags,
                heuristic_tags=mapping.heuristic_tags,
                difficulty_aspects=mapping.difficulty_aspects,
                user_confirmed_key_points=notebook.key_points if notebook else [],
                user_confirmed_stuck_points=notebook.stuck_points if notebook else [],
                user_tags=old.user_tags if old is not None and not force_all else [],
                fingerprint=fingerprint,
                ocr_text_length=len(ocr_text),
                tag_prompt_version=tag_prompt_version,
                topic_path=topic_path,
            )
            result_entries[problem_id] = entry

            if on_progress is not None:
                on_progress(IndexProgress(
                    phase="problem_tag_done",
                    problem_id=problem_id,
                    physics_count=len(mapping.physics_model_tags),
                    math_count=len(mapping.math_technique_tags),
                    heuristic_count=len(mapping.heuristic_tags),
                    topic_path=topic_path or "",
                    problems_processed_so_far=stats.tags_skipped + stats.tags_regenerated + stats.refinement_only,
                ))

            # Stats accounting
            if action == "re_tag_only":
                stats.tags_regenerated += 1
                stats.file_unchanged += 1
                stats.ocr_reused += 1
            elif action in ("re_ocr_and_re_tag", "full_index"):
                if forced_override:
                    stats.forced_regenerations += 1
                else:
                    stats.file_changed += 1
                stats.ocr_regenerated += 1
                stats.tags_regenerated += 1

    write_index(workspace_root / ".cpho" / "index.jsonl", list(result_entries.values()))

    if all_candidates:
        new_count = _merge_candidates(workspace_root, all_candidates)
        stats.candidate_tags_proposed = new_count

    stats.pending_review_items = len(list_pending_candidates(workspace_root))
    if on_progress is not None:
        on_progress(IndexProgress(phase="complete"))
    return stats
