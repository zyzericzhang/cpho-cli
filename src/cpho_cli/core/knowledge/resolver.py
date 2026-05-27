from __future__ import annotations

import os
from pathlib import Path

from cpho_cli.core.index.api import get_problem_entry
from cpho_cli.core.index import ProblemNotIndexedError
from cpho_cli.core.index.vocabulary import load_merged_vocabulary
from cpho_cli.core.knowledge.store import iter_private_knowledge_files, load_knowledge_document
from cpho_cli.models.index import IndexEntry, TagCategory
from cpho_cli.models.knowledge import KnowledgeDocument, KnowledgeMatch, KnowledgeSource


class KnowledgeResolver:
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root

    def find_for_problem(self, problem_id: str) -> list[KnowledgeMatch]:
        entry = get_problem_entry(self.workspace_root, problem_id)
        if entry is None:
            raise ProblemNotIndexedError(f"Not indexed: {problem_id}")

        exact_ids, categories = self._problem_tag_ids_and_categories(entry)
        documents = self._load_documents()
        exact = [
            self._match(document, "exact")
            for document in documents
            if document.frontmatter.canonical_tag_id in exact_ids
        ]
        if exact:
            return self._sort_matches(exact)

        fallback = [
            self._match(document, "same_category")
            for document in documents
            if self._category_for(document.frontmatter.canonical_tag_id) in categories
        ]
        return self._sort_matches(fallback)

    def _problem_tag_ids_and_categories(self, entry: IndexEntry) -> tuple[set[str], set[TagCategory]]:
        vocabulary = load_merged_vocabulary(self.workspace_root)
        ids = {
            ref.internal_id
            for ref in entry.physics_model_tags + entry.math_technique_tags + entry.heuristic_tags
        }
        for user_tag in entry.user_tags:
            ids.update(user_tag.canonical_tags)
        categories = {
            vocabulary.tags[tag_id].category for tag_id in ids if tag_id in vocabulary.tags
        }
        return ids, categories

    def _category_for(self, tag_id: str) -> TagCategory | None:
        vocabulary = load_merged_vocabulary(self.workspace_root)
        tag = vocabulary.tags.get(tag_id)
        return tag.category if tag is not None else None

    def _load_documents(self) -> list[KnowledgeDocument]:
        documents = [
            load_knowledge_document(self.workspace_root, path, source=KnowledgeSource.PRIVATE)
            for path in iter_private_knowledge_files(self.workspace_root)
        ]
        documents.extend(self._load_community_documents())
        return documents

    def _load_community_documents(self) -> list[KnowledgeDocument]:
        default_root = Path.home() / ".cache" / "cpho" / "community-kb"
        root = Path(os.environ.get("CPHO_COMMUNITY_KB_DIR", default_root))
        if not root.exists():
            return []
        documents: list[KnowledgeDocument] = []
        for repo_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            for path in sorted(repo_dir.rglob("*")):
                if not path.is_file():
                    continue
                try:
                    documents.append(
                        load_knowledge_document(
                            self.workspace_root,
                            path,
                            source=KnowledgeSource.COMMUNITY,
                            repo_name=repo_dir.name,
                        )
                    )
                except Exception:
                    continue
        return documents

    def _match(self, document: KnowledgeDocument, match_kind: str) -> KnowledgeMatch:
        return KnowledgeMatch(
            path=document.path,
            canonical_tag_id=document.frontmatter.canonical_tag_id,
            source=document.source,
            repo_name=document.repo_name,
            title=document.frontmatter.title,
            excerpt=document.body[:240],
            match_kind=match_kind,
        )

    def _sort_matches(self, matches: list[KnowledgeMatch]) -> list[KnowledgeMatch]:
        source_order = {KnowledgeSource.PRIVATE: 0, KnowledgeSource.COMMUNITY: 1}
        return sorted(matches, key=lambda item: (source_order[item.source], str(item.path)))
