from __future__ import annotations

from pathlib import Path

from cpho_cli.models.documents import (
    AmbiguousPaperMatch,
    PaperAnswerPair,
    PaperFile,
    PaperKind,
    WorkspaceDiscoveryResult,
)

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
ANSWER_MARKERS = ("answer", "answers", "solution", "solutions", "ans", "key", "答案", "解析")
ANSWER_DIRS = {"answer", "answers", "solutions", "答案"}
PROBLEM_MARKERS = ("problem", "problems", "question", "questions", "试题", "试卷", "题目")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def _is_supported(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def _strip_answer_markers(stem: str) -> str:
    normalized = stem.lower().replace("_", "-").replace(" ", "-")
    parts = [part for part in normalized.split("-") if part]
    filtered = [part for part in parts if part not in ANSWER_MARKERS and part not in PROBLEM_MARKERS]
    text = "-".join(filtered)
    for marker in ("答案", "解析", "试题", "试卷", "题目"):
        text = text.replace(marker, "")
    return text.strip("-")


def _looks_like_answer(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    stem = path.stem.lower()
    return bool(lowered_parts & ANSWER_DIRS) or any(marker in stem for marker in ANSWER_MARKERS)


def _safe_files(root: Path) -> list[Path]:
    resolved_root = root.resolve()
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or not _is_supported(path):
            continue
        resolved = path.resolve()
        try:
            resolved.relative_to(resolved_root)
        except ValueError:
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.as_posix())


def _paper_total_pages(path: Path) -> int:
    if path.suffix.lower() in IMAGE_EXTENSIONS:
        return 1
    if path.suffix.lower() == ".pdf":
        try:
            import fitz

            with fitz.open(path) as document:
                return max(len(document), 1)
        except Exception:
            return 1
    return 1


def _paper_file(path: Path, kind: PaperKind) -> PaperFile:
    return PaperFile(path=path, paper_kind=kind, total_pages=_paper_total_pages(path))


def discover_workspace(root: Path) -> WorkspaceDiscoveryResult:
    files = _safe_files(root)
    answer_paths = [path for path in files if _looks_like_answer(path)]
    problem_paths = [path for path in files if path not in answer_paths]

    pairs: list[PaperAnswerPair] = []
    unmatched: list[PaperFile] = []
    ambiguous: list[AmbiguousPaperMatch] = []
    answers = [_paper_file(path, PaperKind.ANSWER) for path in answer_paths]

    for problem_path in problem_paths:
        problem_key = _strip_answer_markers(problem_path.stem)
        candidates = [
            answer
            for answer in answers
            if _strip_answer_markers(answer.path.stem) == problem_key
        ]
        problem = _paper_file(problem_path, PaperKind.PROBLEM)
        if len(candidates) == 1:
            pairs.append(PaperAnswerPair(paper=problem, answer=candidates[0]))
        elif len(candidates) > 1:
            ambiguous.append(AmbiguousPaperMatch(paper=problem, candidates=candidates))
        else:
            unmatched.append(problem)

    return WorkspaceDiscoveryResult(pairs=pairs, unmatched_problems=unmatched, ambiguous=ambiguous)
