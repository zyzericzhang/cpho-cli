"""Core index exceptions and public surface."""


class IndexBuildError(RuntimeError):
    """Raised when index building or reading fails."""


class IndexNotFoundError(IndexBuildError):
    """Raised when .cpho/index.jsonl is missing."""


class ProblemNotIndexedError(IndexBuildError):
    """Raised when a requested problem is absent from the index."""


class VocabularyError(IndexBuildError):
    """Raised when vocabulary files cannot be loaded or resolved."""
