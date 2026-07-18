"""Knowledge Corpus service: ingestion orchestration and administrator review workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy.orm import Session

from divyadrishti.config import get_settings
from divyadrishti.documents.chunker import SemanticChunker
from divyadrishti.documents.models import Document
from divyadrishti.documents.store import ChromaVectorStore, VectorStore
from divyadrishti.knowledge.book_ingestion import BookIngestionPipeline, BookIngestionReport
from divyadrishti.knowledge.corpus_pipeline import BookMetadata
from divyadrishti.knowledge.graph_builder import KnowledgeGraphBuilder
from divyadrishti.knowledge.hybrid_retrieval import CorpusRetrievalEngine, candidate_rule_to_domain_rule
from divyadrishti.knowledge.repository import KnowledgeRepository
from divyadrishti.knowledge.retrieval import KnowledgeRetrievalEngine
from divyadrishti.knowledge.rule_extraction import CandidateRuleDraft, RuleExtractor
from divyadrishti.models import CandidateRule, CandidateRuleStatus, Corpus, ExtractedBookPage, RuleReviewAudit, UploadedBook
from divyadrishti.repositories import (
    CandidateRuleRepository,
    CorpusRepository,
    ExtractedBookPageRepository,
    KnowledgeGraphRepository,
    RuleReviewAuditRepository,
    UploadedBookRepository,
)

UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "books"


class CorpusIngestionError(Exception):
    """Raised when a book cannot be ingested into the Knowledge Corpus."""


class CorpusService:
    """Administrator-facing service for corpora, book ingestion, and rule review."""

    def __init__(self, db: Session, knowledge_repository: KnowledgeRepository | None = None) -> None:
        self.db = db
        self.settings = get_settings()
        self.corpus_repo = CorpusRepository(db)
        self.book_repo = UploadedBookRepository(db)
        self.candidate_repo = CandidateRuleRepository(db)
        self.audit_repo = RuleReviewAuditRepository(db)
        self.graph_repo = KnowledgeGraphRepository(db)
        self.extracted_page_repo = ExtractedBookPageRepository(db)
        self.graph_builder = KnowledgeGraphBuilder(self.graph_repo)
        self.chunker = SemanticChunker()
        self.rule_extractor = RuleExtractor()
        # The file-based rule repository backing the Reasoning Engine's
        # keyword fallback. Approving a candidate rule persists it here too,
        # so legacy consumers and the keyword-only path both benefit.
        self.knowledge_repository = knowledge_repository

    # ------------------------------------------------------------------
    # Corpora
    # ------------------------------------------------------------------
    def list_corpora(self) -> list[Corpus]:
        return self.corpus_repo.list_all()

    def create_corpus(self, data: dict[str, Any]) -> Corpus:
        corpus = Corpus(**data)
        return self.corpus_repo.create(corpus)

    def get_or_create_default_corpus(self) -> Corpus:
        return self.corpus_repo.get_or_create_default()

    # ------------------------------------------------------------------
    # Book upload + ingestion
    # ------------------------------------------------------------------
    async def upload_book(
        self,
        user_id: int,
        corpus_id: int,
        file: UploadFile,
        metadata: dict[str, Any],
    ) -> UploadedBook:
        """Save an uploaded book file and register it for ingestion."""
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        file_name = file.filename or "uploaded_book"
        file_path = UPLOADS_DIR / f"{corpus_id}_{file_name}"
        with file_path.open("wb") as buffer:
            buffer.write(await file.read())

        book = UploadedBook(
            user_id=user_id,
            corpus_id=corpus_id,
            file_path=str(file_path),
            file_name=file_name,
            title=metadata.get("title") or file_name,
            author=metadata.get("author"),
            publisher=metadata.get("publisher"),
            edition=metadata.get("edition"),
            isbn=metadata.get("isbn"),
            publication_year=metadata.get("publication_year"),
            source=metadata.get("source"),
            language=metadata.get("language_hint"),
            status="pending",
            book_metadata=metadata,
        )
        return self.book_repo.create(book)

    def ingest_book(self, book_id: int) -> BookIngestionReport:
        """Run the book ingestion pipeline for a previously uploaded book.

        Extraction -> OCR fallback (if scanned) -> language detection ->
        hierarchy extraction (title, author, chapter, section, verse, page)
        -> database storage -> semantic chunking -> automatic rule
        extraction -> candidate rules (pending administrator approval).
        """
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise CorpusIngestionError(f"Book {book_id} not found")
        if not book.corpus_id:
            raise CorpusIngestionError(f"Book {book_id} is not attached to a corpus")

        book.status = "processing"
        self.db.commit()

        try:
            pipeline = BookIngestionPipeline(repository=self.extracted_page_repo)
            metadata = BookMetadata(
                title=book.title or book.file_name,
                author=book.author,
                publisher=book.publisher,
                edition=book.edition,
                isbn=book.isbn,
                publication_year=book.publication_year,
                source=book.source,
                language_hint=book.language,
            )
            report = pipeline.ingest(book.file_path, book_id=book.id, metadata=metadata)

            candidate_rules = self._extract_and_store_candidate_rules(book)
            report = report.model_copy(update={"candidate_rule_count": len(candidate_rules)})

            book.status = "completed"
            book.language = report.language_detected
            book.ingestion_report_json = report.model_dump()
            book.processed_at = datetime.now(timezone.utc)
            self.db.commit()
            return report
        except Exception as exc:
            book.status = "failed"
            book.ingestion_report_json = {"error": str(exc)}
            self.db.commit()
            raise CorpusIngestionError(f"Ingestion failed for book {book_id}: {exc}") from exc

    def _extract_and_store_candidate_rules(self, book: UploadedBook) -> list[CandidateRule]:
        """Chunk the extracted pages into semantic chunks and persist candidate rules."""
        pages = self.extracted_page_repo.list_by_book(book.id)
        if not pages:
            return []

        raw_text = "\n\n".join(page.text for page in pages if page.text)
        document = Document(
            source_path=book.file_path,
            file_type=Path(book.file_path).suffix.lower(),
            language=book.language or "",
            title=book.title or book.file_name,
            author=book.author or "",
            raw_text=raw_text,
        )

        chunks = self.chunker.chunk(
            document,
            book_id=str(book.id),
            book_title=book.title or book.file_name,
            author=book.author or "",
        )

        drafts = self.rule_extractor.extract_many(chunks)
        if not drafts:
            return []

        candidates = [
            self._candidate_rule_from_draft(draft, book)
            for draft in drafts
        ]
        return self.candidate_repo.bulk_create(candidates)

    def _candidate_rule_from_draft(
        self, draft: CandidateRuleDraft, book: UploadedBook
    ) -> CandidateRule:
        """Convert a CandidateRuleDraft to a pending CandidateRule row."""
        return CandidateRule(
            candidate_rule_id=draft.candidate_rule_id,
            corpus_id=book.corpus_id,
            book_id=book.id,
            source_book_title=draft.source_book_title,
            language=draft.language,
            chapter=draft.chapter,
            verse=draft.verse,
            page=draft.page,
            original_text=draft.original_text,
            translated_text=draft.translated_text,
            topic=draft.topic,
            subtopic=draft.subtopic,
            astrological_factors_json=draft.astrological_factors.model_dump(),
            candidate_conditions_json=draft.candidate_conditions,
            candidate_interpretation=draft.candidate_interpretation,
            confidence=draft.confidence,
            status=CandidateRuleStatus.PENDING.value,
            chunk_id=draft.chunk_id,
        )

    def _vector_store_for_corpus(self, corpus_id: int) -> VectorStore:
        return ChromaVectorStore(
            collection_name=f"corpus_{corpus_id}",
            persist_dir=self.settings.corpus_vector_store_dir,
        )

    def delete_book(self, book_id: int) -> None:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError("Book not found")
        self.book_repo.delete(book)

    def list_books(self, corpus_id: int | None = None) -> list[UploadedBook]:
        books = self.book_repo.list_all()
        if corpus_id is not None:
            books = [b for b in books if b.corpus_id == corpus_id]
        return books

    # ------------------------------------------------------------------
    # Candidate rule review workflow
    # ------------------------------------------------------------------
    def list_candidate_rules(
        self,
        corpus_id: int | None = None,
        book_id: int | None = None,
        status: str | None = None,
        topic: str | None = None,
    ) -> list[CandidateRule]:
        return self.candidate_repo.list(corpus_id=corpus_id, book_id=book_id, status=status, topic=topic)

    def get_candidate_rule(self, candidate_id: int) -> CandidateRule | None:
        return self.candidate_repo.get_by_id(candidate_id)

    def approve_candidate_rule(self, candidate_id: int, actor_id: int, notes: str | None = None) -> CandidateRule:
        candidate = self._require_candidate(candidate_id)
        previous_state = self._snapshot(candidate)

        candidate.status = CandidateRuleStatus.APPROVED.value
        candidate.reviewed_by = actor_id
        candidate.reviewed_at = datetime.now(timezone.utc)
        candidate.review_notes = notes
        candidate.approved_rule_id = candidate.approved_rule_id or f"CORPUS_{candidate.candidate_rule_id}"
        self.candidate_repo.update(candidate)

        # Extend (not replace) the existing file-based rule repository so
        # the keyword-fallback path and any legacy consumers benefit too.
        if self.knowledge_repository is not None:
            domain_rule = candidate_rule_to_domain_rule(candidate)
            if not self.knowledge_repository.get_rule(domain_rule.rule_id):
                self.knowledge_repository.add_rule(domain_rule, save=True)

        self._update_rule_node_status(candidate)
        self._log_audit(candidate, actor_id, "approve", previous_state, notes)
        return candidate

    def reject_candidate_rule(self, candidate_id: int, actor_id: int, notes: str | None = None) -> CandidateRule:
        candidate = self._require_candidate(candidate_id)
        previous_state = self._snapshot(candidate)

        candidate.status = CandidateRuleStatus.REJECTED.value
        candidate.reviewed_by = actor_id
        candidate.reviewed_at = datetime.now(timezone.utc)
        candidate.review_notes = notes
        self.candidate_repo.update(candidate)

        self._update_rule_node_status(candidate)
        self._log_audit(candidate, actor_id, "reject", previous_state, notes)
        return candidate

    def deprecate_candidate_rule(self, candidate_id: int, actor_id: int, notes: str | None = None) -> CandidateRule:
        candidate = self._require_candidate(candidate_id)
        previous_state = self._snapshot(candidate)

        candidate.status = CandidateRuleStatus.DEPRECATED.value
        candidate.reviewed_by = actor_id
        candidate.reviewed_at = datetime.now(timezone.utc)
        candidate.review_notes = notes
        self.candidate_repo.update(candidate)

        if self.knowledge_repository is not None and candidate.approved_rule_id:
            rule = self.knowledge_repository.get_rule(candidate.approved_rule_id)
            if rule:
                rule.deprecated = True
                rule.enabled = False
                self.knowledge_repository.update_rule(rule)

        self._update_rule_node_status(candidate)
        self._log_audit(candidate, actor_id, "deprecate", previous_state, notes)
        return candidate

    def merge_candidate_rule(
        self, candidate_id: int, target_candidate_id: int, actor_id: int, notes: str | None = None
    ) -> CandidateRule:
        candidate = self._require_candidate(candidate_id)
        target = self._require_candidate(target_candidate_id)
        previous_state = self._snapshot(candidate)

        candidate.status = CandidateRuleStatus.MERGED.value
        candidate.merged_into_candidate_id = target.id
        candidate.reviewed_by = actor_id
        candidate.reviewed_at = datetime.now(timezone.utc)
        candidate.review_notes = notes
        # Merge distinguishing detail into the target's astrological factors
        # so no structured information from the merged candidate is lost.
        merged_factors = dict(target.astrological_factors_json or {})
        for key, values in (candidate.astrological_factors_json or {}).items():
            merged_factors[key] = list(dict.fromkeys((merged_factors.get(key, []) or []) + (values or [])))
        target.astrological_factors_json = merged_factors
        target.candidate_conditions_json = list(
            dict.fromkeys((target.candidate_conditions_json or []) + (candidate.candidate_conditions_json or []))
        )

        self.candidate_repo.update(candidate)
        self.candidate_repo.update(target)

        self._log_audit(candidate, actor_id, "merge", previous_state, notes, new_state={"merged_into": target.id})
        return candidate

    def edit_candidate_rule(
        self, candidate_id: int, actor_id: int, updates: dict[str, Any], notes: str | None = None
    ) -> CandidateRule:
        candidate = self._require_candidate(candidate_id)
        previous_state = self._snapshot(candidate)

        if "candidate_conditions" in updates and updates["candidate_conditions"] is not None:
            candidate.candidate_conditions_json = updates["candidate_conditions"]
        for field_name in ("topic", "subtopic", "candidate_interpretation", "confidence"):
            if updates.get(field_name) is not None:
                setattr(candidate, field_name, updates[field_name])

        candidate.version += 1
        self.candidate_repo.update(candidate)

        self._log_audit(candidate, actor_id, "edit", previous_state, notes)
        return candidate

    def annotate_candidate_rule(self, candidate_id: int, actor_id: int, comment: str) -> RuleReviewAudit:
        candidate = self._require_candidate(candidate_id)
        return self._log_audit(candidate, actor_id, "annotate", None, comment)

    def get_audit_trail(self, candidate_id: int) -> list[RuleReviewAudit]:
        return self.audit_repo.list_for_candidate(candidate_id)

    def compare_candidate_rules(self, left_id: int, right_id: int) -> dict[str, Any]:
        left = self._require_candidate(left_id)
        right = self._require_candidate(right_id)
        self._log_audit(left, None, "compare", None, f"Compared against candidate {right_id}")

        fields = [
            "topic",
            "subtopic",
            "candidate_interpretation",
            "candidate_conditions_json",
            "astrological_factors_json",
            "confidence",
            "status",
        ]
        differences: dict[str, dict[str, Any]] = {}
        for field_name in fields:
            left_value = getattr(left, field_name)
            right_value = getattr(right, field_name)
            if left_value != right_value:
                differences[field_name] = {"left": left_value, "right": right_value}

        return {"left": left, "right": right, "differences": differences}

    # ------------------------------------------------------------------
    # Retrieval + graph
    # ------------------------------------------------------------------
    def build_retrieval_engine(
        self, corpus_ids: list[int] | None = None, keyword_engine: KnowledgeRetrievalEngine | None = None
    ) -> CorpusRetrievalEngine:
        """Build a hybrid retrieval engine scoped to the given corpora (or all)."""
        corpora = self.corpus_repo.list_all()
        if corpus_ids is not None:
            corpora = [c for c in corpora if c.id in corpus_ids]

        approved = self.candidate_repo.list_approved_for_corpora([c.id for c in corpora])
        corpus_authority = {c.id: c.authority_weight for c in corpora}
        corpus_names = {c.id: c.name for c in corpora}

        vector_store: VectorStore | None = None
        embedder = None
        if corpora:
            try:
                vector_store = self._vector_store_for_corpus(corpora[0].id)
                from divyadrishti.documents.embeddings import get_embedding_provider

                embedder = get_embedding_provider(
                    self.settings.embedding_provider, **(
                        {"model_name": self.settings.embedding_model} if self.settings.embedding_model else {}
                    )
                )
            except Exception:
                vector_store = None
                embedder = None

        return CorpusRetrievalEngine(
            vector_store=vector_store,
            embedder=embedder,
            approved_candidates=approved,
            corpus_authority=corpus_authority,
            corpus_names=corpus_names,
            keyword_engine=keyword_engine,
        )

    def traverse_graph(
        self, node_type: str, ref_id: str, depth: int = 2, corpus_id: int | None = None
    ) -> dict[str, Any]:
        return self.graph_repo.traverse(node_type, ref_id, depth=depth, corpus_id=corpus_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _require_candidate(self, candidate_id: int) -> CandidateRule:
        candidate = self.candidate_repo.get_by_id(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate rule {candidate_id} not found")
        return candidate

    def _snapshot(self, candidate: CandidateRule) -> dict[str, Any]:
        return {
            "status": candidate.status,
            "topic": candidate.topic,
            "subtopic": candidate.subtopic,
            "candidate_interpretation": candidate.candidate_interpretation,
            "candidate_conditions_json": candidate.candidate_conditions_json,
            "confidence": candidate.confidence,
        }

    def _log_audit(
        self,
        candidate: CandidateRule,
        actor_id: int | None,
        action: str,
        previous_state: dict[str, Any] | None,
        comment: str | None,
        new_state: dict[str, Any] | None = None,
    ) -> RuleReviewAudit:
        entry = RuleReviewAudit(
            candidate_rule_id=candidate.id,
            actor_id=actor_id,
            action=action,
            comment=comment,
            previous_state_json=previous_state,
            new_state_json=new_state or self._snapshot(candidate),
        )
        return self.audit_repo.create(entry)

    def _update_rule_node_status(self, candidate: CandidateRule) -> None:
        node = self.graph_repo.find_node(candidate.corpus_id, "rule", candidate.candidate_rule_id)
        if node:
            self.graph_repo.update_node_metadata(node, {"status": candidate.status})

