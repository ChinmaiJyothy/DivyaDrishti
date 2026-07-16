"""Knowledge graph repository supporting node creation and BFS traversal."""

from __future__ import annotations

from collections import deque

from sqlalchemy.orm import Session

from divyadrishti.models import KnowledgeGraphEdge, KnowledgeGraphNode


class KnowledgeGraphRepository:
    """Database operations for knowledge graph nodes and edges."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create_node(
        self,
        corpus_id: int,
        node_type: str,
        ref_id: str,
        label: str,
        metadata: dict | None = None,
    ) -> KnowledgeGraphNode:
        existing = (
            self.db.query(KnowledgeGraphNode)
            .filter(
                KnowledgeGraphNode.corpus_id == corpus_id,
                KnowledgeGraphNode.node_type == node_type,
                KnowledgeGraphNode.ref_id == ref_id,
            )
            .first()
        )
        if existing:
            return existing

        node = KnowledgeGraphNode(
            corpus_id=corpus_id,
            node_type=node_type,
            ref_id=ref_id,
            label=label,
            node_metadata_json=metadata or {},
        )
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node

    def add_edge(
        self,
        corpus_id: int,
        source_node: KnowledgeGraphNode,
        target_node: KnowledgeGraphNode,
        relation: str,
    ) -> KnowledgeGraphEdge:
        existing = (
            self.db.query(KnowledgeGraphEdge)
            .filter(
                KnowledgeGraphEdge.source_node_id == source_node.id,
                KnowledgeGraphEdge.target_node_id == target_node.id,
                KnowledgeGraphEdge.relation == relation,
            )
            .first()
        )
        if existing:
            return existing

        edge = KnowledgeGraphEdge(
            corpus_id=corpus_id,
            source_node_id=source_node.id,
            target_node_id=target_node.id,
            relation=relation,
        )
        self.db.add(edge)
        self.db.commit()
        self.db.refresh(edge)
        return edge

    def update_node_metadata(self, node: KnowledgeGraphNode, metadata: dict) -> KnowledgeGraphNode:
        node.node_metadata_json = {**(node.node_metadata_json or {}), **metadata}
        self.db.commit()
        self.db.refresh(node)
        return node

    def find_node(self, corpus_id: int, node_type: str, ref_id: str) -> KnowledgeGraphNode | None:
        return (
            self.db.query(KnowledgeGraphNode)
            .filter(
                KnowledgeGraphNode.corpus_id == corpus_id,
                KnowledgeGraphNode.node_type == node_type,
                KnowledgeGraphNode.ref_id == ref_id,
            )
            .first()
        )

    def traverse(
        self,
        node_type: str,
        ref_id: str,
        depth: int = 2,
        corpus_id: int | None = None,
    ) -> dict:
        """Breadth-first traversal of the graph starting at the given node.

        Returns a dict with ``nodes`` and ``edges`` describing the reachable
        subgraph up to ``depth`` hops in either direction.
        """
        query = self.db.query(KnowledgeGraphNode).filter(
            KnowledgeGraphNode.node_type == node_type, KnowledgeGraphNode.ref_id == ref_id
        )
        if corpus_id is not None:
            query = query.filter(KnowledgeGraphNode.corpus_id == corpus_id)
        start_nodes = query.all()
        if not start_nodes:
            return {"nodes": [], "edges": []}

        visited_node_ids: set[int] = set()
        visited_edge_ids: set[int] = set()
        queue: deque[tuple[KnowledgeGraphNode, int]] = deque((n, 0) for n in start_nodes)
        result_nodes: list[KnowledgeGraphNode] = []
        result_edges: list[KnowledgeGraphEdge] = []

        while queue:
            node, current_depth = queue.popleft()
            if node.id in visited_node_ids:
                continue
            visited_node_ids.add(node.id)
            result_nodes.append(node)

            if current_depth >= depth:
                continue

            for edge in list(node.outgoing_edges) + list(node.incoming_edges):
                if edge.id in visited_edge_ids:
                    continue
                visited_edge_ids.add(edge.id)
                result_edges.append(edge)

                neighbor = edge.target_node if edge.source_node_id == node.id else edge.source_node
                if neighbor.id not in visited_node_ids:
                    queue.append((neighbor, current_depth + 1))

        return {
            "nodes": [
                {
                    "id": n.id,
                    "node_type": n.node_type,
                    "ref_id": n.ref_id,
                    "label": n.label,
                    "metadata": n.node_metadata_json,
                }
                for n in result_nodes
            ],
            "edges": [
                {
                    "id": e.id,
                    "source_node_id": e.source_node_id,
                    "target_node_id": e.target_node_id,
                    "relation": e.relation,
                }
                for e in result_edges
            ],
        }
