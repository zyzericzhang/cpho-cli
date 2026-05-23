"""Core index exceptions and public surface."""


class IndexBuildError(RuntimeError):
    """Raised when index building or reading fails."""


class IndexNotFoundError(IndexBuildError):
    """Raised when .cpho/index.jsonl is missing."""


class ProblemNotIndexedError(IndexBuildError):
    """Raised when a requested problem is absent from the index."""


class VocabularyError(IndexBuildError):
    """Raised when vocabulary files cannot be loaded or resolved."""


# --- Re-exports (populated by 02-05 T1/T2) ---

from cpho_cli.core.index.api import (  # noqa: E402
    find_related_problems,
    get_problem_entry,
    query_index,
)
from cpho_cli.core.index.notebook import get_problem_notes, set_problem_notes  # noqa: E402
from cpho_cli.core.index.ocr_cache import (  # noqa: E402
    OcrEngineDelta,
    OcrUpgradeDecisionRequired,
)
from cpho_cli.core.index.vocabulary import (  # noqa: E402
    list_pending_candidates,
    load_merged_vocabulary as load_vocabulary,
)
from cpho_cli.models.index import (  # noqa: E402
    CandidateTag,
    CanonicalTag,
    IndexEntry,
    IndexRunStats,
    TagCategory,
    TagLayer,
    TagSource,
    TagStatus,
    TagVisibility,
    UserNotebookEntry,
    Vocabulary,
)

__all__ = [
    # Exceptions
    "IndexBuildError",
    "IndexNotFoundError",
    "ProblemNotIndexedError",
    "VocabularyError",
    # API
    "query_index",
    "get_problem_entry",
    "find_related_problems",
    # Notebook
    "get_problem_notes",
    "set_problem_notes",
    # Vocabulary
    "load_vocabulary",
    "list_pending_candidates",
    # OCR
    "OcrUpgradeDecisionRequired",
    "OcrEngineDelta",
    # Models
    "IndexEntry",
    "IndexRunStats",
    "Vocabulary",
    "CanonicalTag",
    "CandidateTag",
    "UserNotebookEntry",
    "TagCategory",
    "TagVisibility",
    "TagStatus",
    "TagLayer",
    "TagSource",
]
