"""Document Knowledge Processing Pipeline orchestrator."""

from pathlib import Path
from typing import Any

from divyadrishti.documents.chunker import SemanticChunker
from divyadrishti.documents.embeddings import EmbeddingProvider, MockEmbeddingProvider
from divyadrishti.documents.extractors import ExtractorFactory
from divyadrishti.documents.language import IdentityTranslator, LanguageDetector, TranslatorProvider
from divyadrishti.documents.models import (
    Document,
    DocumentProcessingResult,
)
from divyadrishti.documents.store import InMemoryVectorStore, VectorStore


class DocumentProcessingPipeline:
    """End-to-end pipeline for transforming documents into structured knowledge."""

    def __init__(
        self,
        extractor_factory: ExtractorFactory | None = None,
        chunker: SemanticChunker | None = None,
        language_detector: LanguageDetector | None = None,
        translator: TranslatorProvider | None = None,
        embedder: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.extractor_factory = extractor_factory or ExtractorFactory()
        self.chunker = chunker or SemanticChunker()
        self.language_detector = language_detector or LanguageDetector()
        self.translator = translator or IdentityTranslator()
        self.embedder = embedder or MockEmbeddingProvider()
        self.vector_store = vector_store or InMemoryVectorStore()

    def process(
        self,
        file_path: Path | str,
        book_id: str = "",
        book_title: str = "",
        author: str = "",
        metadata: dict[str, Any] | None = None,
        ocr_enabled: bool = False,
        translate_to: str | None = None,
    ) -> DocumentProcessingResult:
        """Process a single document and store its chunks."""
        path = Path(file_path)
        errors: list[str] = []
        stored = False

        try:
            extractor = self.extractor_factory.get_extractor(path, ocr_enabled=ocr_enabled)
            raw_text = extractor.extract(path)
        except Exception as exc:
            errors.append(f"Extraction failed: {exc}")
            raw_text = ""

        language = self.language_detector.detect(raw_text)

        document = Document(
            source_path=str(path),
            file_type=path.suffix.lower(),
            language=language,
            title=book_title or path.stem,
            author=author,
            metadata=metadata or {},
            raw_text=raw_text,
        )

        chunks = self.chunker.chunk(document, book_id=book_id, book_title=book_title, author=author)

        for chunk in chunks:
            chunk.metadata.source_file = str(path)
            if translate_to and language != translate_to:
                chunk.metadata.translated_text = self.translator.translate(
                    chunk.metadata.original_text or chunk.text,
                    target_lang=translate_to,
                )

            embedding_text = chunk.metadata.translated_text or chunk.text
            chunk.embedding = self.embedder.embed(embedding_text)
            chunk.citation = chunk.build_citation()

        document.chunks = chunks

        if chunks:
            try:
                self.vector_store.add(chunks)
                stored = True
            except Exception as exc:
                errors.append(f"Vector store failed: {exc}")

        return DocumentProcessingResult(
            document=document,
            chunk_count=len(chunks),
            language=language,
            stored=stored,
            errors=errors,
        )

    def process_directory(
        self,
        directory: Path | str,
        metadata_map: dict[str, dict[str, Any]] | None = None,
        ocr_enabled: bool = False,
        translate_to: str | None = None,
    ) -> list[DocumentProcessingResult]:
        """Process all supported files in a directory."""
        results: list[DocumentProcessingResult] = []
        for path in Path(directory).iterdir():
            if path.is_file() and path.suffix.lower() in {".pdf", ".md", ".txt"}:
                meta = metadata_map.get(path.stem, {}) if metadata_map else {}
                results.append(
                    self.process(
                        path,
                        book_id=meta.get("book_id", path.stem),
                        book_title=meta.get("title", path.stem),
                        author=meta.get("author", ""),
                        metadata=meta,
                        ocr_enabled=ocr_enabled,
                        translate_to=translate_to,
                    )
                )
        return results
