"""Knowledge graph construction for the Knowledge Corpus.

Builds Book -> Chapter -> Verse -> Rule -> {Planet, House, Sign,
Nakshatra, Dasha, Yoga, Dosha, Topic} nodes and edges so that reasoning
and explainability can traverse from a rule back to its classical
source, or from an astrological entity forward to every rule that
mentions it.
"""

from divyadrishti.models import CandidateRule, KnowledgeGraphNode, UploadedBook
from divyadrishti.repositories.knowledge_graph import KnowledgeGraphRepository


class KnowledgeGraphBuilder:
    """Populate the knowledge graph from a book and its candidate/approved rules."""

    def __init__(self, graph_repository: KnowledgeGraphRepository) -> None:
        self.graph_repository = graph_repository

    def add_book(self, corpus_id: int, book: UploadedBook) -> KnowledgeGraphNode:
        return self.graph_repository.get_or_create_node(
            corpus_id=corpus_id,
            node_type="book",
            ref_id=str(book.id),
            label=book.title or book.file_name,
            metadata={"author": book.author, "language": book.language},
        )

    def add_rule(
        self,
        corpus_id: int,
        book: UploadedBook,
        rule: CandidateRule,
    ) -> KnowledgeGraphNode:
        """Add a rule node and connect it to its book, chapter, verse, and entities."""
        book_node = self.add_book(corpus_id, book)

        parent_node = book_node
        if rule.chapter:
            chapter_node = self.graph_repository.get_or_create_node(
                corpus_id=corpus_id,
                node_type="chapter",
                ref_id=f"{book.id}:{rule.chapter}",
                label=f"Chapter {rule.chapter}",
                metadata={"book_id": book.id},
            )
            self.graph_repository.add_edge(corpus_id, book_node, chapter_node, "contains")
            parent_node = chapter_node

        if rule.verse:
            verse_node = self.graph_repository.get_or_create_node(
                corpus_id=corpus_id,
                node_type="verse",
                ref_id=f"{book.id}:{rule.chapter}:{rule.verse}",
                label=f"Verse {rule.verse}",
                metadata={"book_id": book.id, "chapter": rule.chapter, "page": rule.page},
            )
            self.graph_repository.add_edge(corpus_id, parent_node, verse_node, "contains")
            parent_node = verse_node

        rule_node = self.graph_repository.get_or_create_node(
            corpus_id=corpus_id,
            node_type="rule",
            ref_id=rule.candidate_rule_id,
            label=rule.candidate_interpretation[:80],
            metadata={"status": rule.status, "confidence": rule.confidence, "topic": rule.topic},
        )
        self.graph_repository.add_edge(corpus_id, parent_node, rule_node, "contains")

        factors = rule.astrological_factors_json or {}
        self._connect_entities(corpus_id, rule_node, "planet", factors.get("planets", []))
        self._connect_entities(
            corpus_id, rule_node, "house", [str(h) for h in factors.get("houses", [])]
        )
        self._connect_entities(corpus_id, rule_node, "sign", factors.get("signs", []))
        self._connect_entities(corpus_id, rule_node, "nakshatra", factors.get("nakshatras", []))
        self._connect_entities(corpus_id, rule_node, "dasha", factors.get("dashas", []))
        self._connect_entities(corpus_id, rule_node, "yoga", factors.get("yogas", []))
        self._connect_entities(corpus_id, rule_node, "dosha", factors.get("doshas", []))
        self._connect_entities(corpus_id, rule_node, "topic", [rule.topic] if rule.topic else [])

        return rule_node

    def _connect_entities(
        self,
        corpus_id: int,
        rule_node: KnowledgeGraphNode,
        node_type: str,
        values: list[str],
    ) -> None:
        for value in values:
            if not value:
                continue
            entity_node = self.graph_repository.get_or_create_node(
                corpus_id=corpus_id,
                node_type=node_type,
                ref_id=value,
                label=value,
            )
            self.graph_repository.add_edge(corpus_id, rule_node, entity_node, "mentions")
