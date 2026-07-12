# Document Knowledge Processing Pipeline

This module transforms multilingual Vedic astrology books into a structured, retrievable knowledge source.

## Supported Formats

- PDF
- Scanned PDF (via OCR, requires Tesseract)
- Markdown
- TXT
- Future: EPUB, DOCX

## Supported Languages

The pipeline detects language automatically and preserves the original text.

- English
- Sanskrit
- Kannada
- Hindi
- Telugu
- Tamil
- Malayalam
- Gujarati
- Marathi

## Pipeline

For every uploaded document:

1. Extract text.
2. OCR if scanned and OCR enabled.
3. Detect language.
4. Extract metadata.
5. Split into semantic chunks.
6. Generate embeddings.
7. Store embeddings in vector store.
8. Store original text.
9. Optionally translate text.
10. Generate citations.

## Components

- `extractors.py` — `PDFExtractor`, `ScannedPDFExtractor`, `MarkdownExtractor`, `TextExtractor`
- `language.py` — `LanguageDetector`, `TranslatorProvider`, `DeepTranslatorProvider`
- `chunker.py` — `SemanticChunker`
- `embeddings.py` — `EmbeddingProvider`, `MockEmbeddingProvider`, `SentenceTransformerEmbeddingProvider`
- `store.py` — `VectorStore`, `InMemoryVectorStore`, `ChromaVectorStore`
- `retrieval.py` — `DocumentRetrievalEngine` (topic, house, planet, yoga, dosha, semantic, hybrid, citation)
- `pipeline.py` — `DocumentProcessingPipeline` orchestrator

## Usage

```python
from divyadrishti.documents import (
    DocumentProcessingPipeline,
    ChromaVectorStore,
    SentenceTransformerEmbeddingProvider,
    DocumentRetrievalEngine,
)

pipeline = DocumentProcessingPipeline(
    embedder=SentenceTransformerEmbeddingProvider(),
    vector_store=ChromaVectorStore(persist_dir=".chroma"),
)

result = pipeline.process("book.pdf", book_id="BPHS", book_title="Brihat Parashara Hora Shastra")

engine = DocumentRetrievalEngine(pipeline.vector_store, pipeline.embedder)
results = engine.semantic_search("marriage and 7th house")
```

## Primary Knowledge Source

Documents processed by this pipeline become the primary source of truth. The LLM prioritizes retrieved chunks over general knowledge and cites the source whenever possible.
