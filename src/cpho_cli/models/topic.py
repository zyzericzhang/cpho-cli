from __future__ import annotations

from pydantic import Field

from cpho_cli.models.config import StrictModel


class TopicNode(StrictModel):
    id: str
    display_zh: str
    children: list[TopicNode] = Field(default_factory=list)


TopicNode.model_rebuild()


class TopicTaxonomy(StrictModel):
    version: str
    roots: list[TopicNode]

    def flatten_paths(self) -> list[str]:
        """Return all paths (leaf and non-leaf) as display_zh slash-separated strings."""
        result: list[str] = []

        def _walk(nodes: list[TopicNode], prefix: str) -> None:
            for node in nodes:
                path = f"{prefix}/{node.display_zh}" if prefix else node.display_zh
                result.append(path)
                _walk(node.children, path)

        _walk(self.roots, "")
        return result

    def find_node_by_path(self, path: str) -> TopicNode | None:
        """Find a node by slash-separated display_zh path. Returns None if invalid."""
        parts = path.split("/")
        nodes = self.roots
        current: TopicNode | None = None
        for part in parts:
            found = None
            for node in nodes:
                if node.display_zh == part:
                    found = node
                    break
            if found is None:
                return None
            current = found
            nodes = found.children
        return current
