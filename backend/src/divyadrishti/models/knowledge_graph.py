"""Knowledge graph node/edge models for the Knowledge Corpus.

The graph connects Books -> Chapters -> Verses -> Rules -> astrological
entities (Planets, Houses, Signs, Nakshatras, Dashas, Yogas, Doshas,
Topics), enabling graph traversal for explainability and retrieval.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from divyadrishti.database.database import Base


class KnowledgeGraphNode(Base):
    """A node in the knowledge graph (book, chapter, verse, rule, or entity)."""

    __tablename__ = "knowledge_graph_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    corpus_id: Mapped[int] = mapped_column(ForeignKey("corpora.id"), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # book | chapter | verse | rule | planet | house | sign | nakshatra | dasha | yoga | dosha | topic
    ref_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    node_metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    outgoing_edges: Mapped[list["KnowledgeGraphEdge"]] = relationship(
        "KnowledgeGraphEdge",
        foreign_keys="KnowledgeGraphEdge.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    incoming_edges: Mapped[list["KnowledgeGraphEdge"]] = relationship(
        "KnowledgeGraphEdge",
        foreign_keys="KnowledgeGraphEdge.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )


class KnowledgeGraphEdge(Base):
    """A directed, labeled relationship between two knowledge graph nodes."""

    __tablename__ = "knowledge_graph_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    corpus_id: Mapped[int] = mapped_column(ForeignKey("corpora.id"), nullable=False, index=True)
    source_node_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_graph_nodes.id"), nullable=False, index=True
    )
    target_node_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_graph_nodes.id"), nullable=False, index=True
    )
    relation: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # contains | cites | mentions | influences
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    source_node: Mapped["KnowledgeGraphNode"] = relationship(
        "KnowledgeGraphNode", foreign_keys=[source_node_id], back_populates="outgoing_edges"
    )
    target_node: Mapped["KnowledgeGraphNode"] = relationship(
        "KnowledgeGraphNode", foreign_keys=[target_node_id], back_populates="incoming_edges"
    )
