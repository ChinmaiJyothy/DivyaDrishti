"""Knowledge Corpus book ingestion pipeline.

Orchestrates the full pipeline described in the Knowledge Corpus spec:

    Validate -> OCR (if required) -> Language Detection -> Metadata
    -> Semantic Chunking (chapter/verse/page aware) -> Embedding
    -> Vector Store -> Rule Extraction -> Ingestion Report

This module builds on the existing Document Knowledge Processing
Pipeline (`divyadrishti.documents`) rather than duplicating extraction,
chunking, or embedding logic. It NEVER defaults to
``MockEmbeddingProvider`` — a real production embedding provider must
be supplied or configured.
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from divyadrishti.documents.chunker import SemanticChunker
from divyadrishti.documents.embeddings import EmbeddingProvider, get_embedding_provider
from divyadrishti.documents.extractors import ExtractorFactory
from divyadrishti.documents.language import IdentityTranslator, LanguageDetector, TranslatorProvider
from divyadrishti.documents.models import Document, DocumentChunk
from divyadrishti.documents.store import VectorStore
from divyadrishti.knowledge.rule_extraction import CandidateRuleDraft, RuleExtractor

SUPPORTED_LANGUAGES = {
    "en",
    "sa",  # Sanskrit
    "kn",  # Kannada
    "hi",  # Hindi
    "te",  # Telugu
    "ta",  # Tamil
    "ml",  # Malayalam
    "gu",  # Gujarati
    "mr",  # Marathi
}


class BookMetadata(BaseModel):
    """Bibliographic metadata supplied by the administrator at upload time."""

    title: str
    author: str | None = None
    publisher: str | None = None
    edition: str | None = None
    isbn: str | None = None
    publication_year: int | None = None
    source: str | None = None
    language_hint: str | None = None


class IngestionReport(BaseModel):
    """Summary of a single book ingestion run."""

    book_title: str
    language_detected: str
    ocr_used: bool
    page_count: int
    chunk_count: int
    candidate_rule_count: int
    embedding_provider: str
    stored_in_vector_store: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CorpusIngestionResult(BaseModel):
    """Full result of ingesting a book into the Knowledge Corpus."""

    document: Document
    chunks: list[DocumentChunk]
    candidate_rules: list[CandidateRuleDraft]
    report: IngestionReport

    model_config = {"arbitrary_types_allowed": True}


class CorpusIngestionPipeline:
    """End-to-end ingestion pipeline for a single Knowledge Corpus book."""

    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_store: VectorStore,
        chunker: SemanticChunker | None = None,
        language_detector: LanguageDetector | None = None,
        translator: TranslatorProvider | None = None,
        rule_extractor: RuleExtractor | None = None,
    ) -> None:
        if embedder is None:
            raise ValueError(
                "CorpusIngestionPipeline requires a real EmbeddingProvider. "
                "Use divyadrishti.documents.get_embedding_provider(...); "
                "MockEmbeddingProvider must never be used in production ingestion."
            )
        self.embedder = embedder
        self.vector_store = vector_store
        self.chunker = chunker or SemanticChunker()
        self.language_detector = language_detector or LanguageDetector()
        self.translator = translator or IdentityTranslator()
        self.rule_extractor = rule_extractor or RuleExtractor()

    @classmethod
    def from_settings(
        cls,
        vector_store: VectorStore,
        embedding_provider_name: str,
        embedding_model: str | None = None,
        **kwargs: Any,
    ) -> "CorpusIngestionPipeline":
        """Build a pipeline using a configured production embedding provider."""
        provider_kwargs: dict[str, Any] = {}
        if embedding_model:
            provider_kwargs["model_name"] = embedding_model
        embedder = get_embedding_provider(embedding_provider_name, **provider_kwargs)
        return cls(embedder=embedder, vector_store=vector_store, **kwargs)

    def ingest(
        self,
        file_path: Path | str,
        book_id: str,
        metadata: BookMetadata,
        translate_to: str | None = None,
    ) -> CorpusIngestionResult:
        """Run the full ingestion pipeline for a single book file."""
        path = Path(file_path)
        errors: list[str] = []
        warnings: list[str] = []

        if not path.exists():
            raise FileNotFoundError(f"Book file not found: {path}")
        if path.stat().st_size == 0:
            raise ValueError(f"Book file is empty: {path}")

        try:
            extractor, ocr_used = ExtractorFactory.get_extractor_with_ocr_detection(
                path, language_hint=metadata.language_hint
            )
            pages = extractor.extract_pages(path)
        except Exception as exc:
            errors.append(f"Extraction failed: {exc}")
            pages = []
            ocr_used = False

        raw_text = "\n\n".join(text for _, text in pages)

        if raw_text.strip():
            try:
                language = self.language_detector.detect(raw_text)
            except Exception as exc:
                warnings.append(f"Language detection failed, using hint: {exc}")
                language = metadata.language_hint or "unknown"
        else:
            language = metadata.language_hint or "unknown"
            warnings.append("No extractable text found in document.")

        if language not in SUPPORTED_LANGUAGES and language != "unknown":
            warnings.append(
                f"Detected language '{language}' is outside the officially supported set "
                f"{sorted(SUPPORTED_LANGUAGES)}; results may be less accurate."
            )

        document = Document(
            source_path=str(path),
            file_type=path.suffix.lower(),
            language=language,
            title=metadata.title,
            author=metadata.author or "",
            metadata=metadata.model_dump(exclude_none=True),
            raw_text=raw_text,
        )

        chunks = self.chunker.chunk_pages(
            pages,
            document,
            book_id=book_id,
            book_title=metadata.title,
            author=metadata.author or "",
            source_file=str(path),
        )

        for chunk in chunks:
            if translate_to and language != translate_to and language != "unknown":
                try:
                    chunk.metadata.translated_text = self.translator.translate(
                        chunk.metadata.original_text or chunk.text, target_lang=translate_to
                    )
                except Exception as exc:
                    warnings.append(f"Translation failed for chunk {chunk.id}: {exc}")

            embedding_text = chunk.metadata.translated_text or chunk.text
            try:
                chunk.embedding = self.embedder.embed(embedding_text)
            except Exception as exc:
                errors.append(f"Embedding failed for chunk {chunk.id}: {exc}")
            chunk.citation = chunk.build_citation()

        document.chunks = chunks

        stored = False
        if chunks:
            try:
                self.vector_store.add([c for c in chunks if c.embedding])
                stored = True
            except Exception as exc:
                errors.append(f"Vector store write failed: {exc}")

        candidate_rules = self.rule_extractor.extract_many(chunks)

        report = IngestionReport(
            book_title=metadata.title,
            language_detected=language,
            ocr_used=ocr_used,
            page_count=len(pages),
            chunk_count=len(chunks),
            candidate_rule_count=len(candidate_rules),
            embedding_provider=self.embedder.__class__.__name__,
            stored_in_vector_store=stored,
            errors=errors,
            warnings=warnings,
        )

        return CorpusIngestionResult(
            document=document,
            chunks=chunks,
            candidate_rules=candidate_rules,
            report=report,
        )
