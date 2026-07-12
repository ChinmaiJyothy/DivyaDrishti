# Document Knowledge Processing Pipeline

## Overview

The Document Knowledge Processing Pipeline transforms multilingual Vedic astrology books into a structured, retrievable knowledge source. It is the primary source of truth for DivyaDrishti's AI.

## Supported Formats

- PDF
- Scanned PDF (via OCR, requires Tesseract)
- Markdown
- TXT
- Future: EPUB, DOCX

## Supported Languages

The pipeline detects language automatically and always preserves the original text.

- English
- Sanskrit
- Kannada
- Hindi
- Telugu
- Tamil
- Malayalam
- Gujarati
- Marathi

## Pipeline Steps

1. **Extract text** from the source file.
2. **OCR** if the PDF is scanned and OCR is enabled.
3. **Detect language** of the extracted text.
4. **Extract metadata** (book, author, chapter, section, verse, page, topics, keywords).
5. **Split into semantic chunks** preserving headings and context.
6. **Generate embeddings** for each chunk.
7. **Store embeddings** in a vector store.
8. **Store original text** in chunk metadata.
9. **Store translated text** (optional).
10. **Generate citations** for every chunk.

## Chunk Metadata

Each chunk carries:

| Field | Description |
|-------|-------------|
| chunk_id | Unique identifier |
| book_id | Book identifier |
| book_title | Book title |
| author | Author name |
| language | Detected language |
| chapter | Chapter reference |
| section | Section/heading |
| verse | Verse reference |
| page_number | Page number |
| topics | Topic tags |
| subtopics | Subtopic tags |
| keywords | Keywords |
| original_text | Original chunk text |
| translated_text | Translated text (optional) |
| source_file | Source file path |
| chunk_index | Position in the document |

## Retrieval Capabilities

- `semantic_search(query)`
- `search_by_topic(topic)`
- `search_by_house(house)`
- `search_by_planet(planet)`
- `search_by_yoga(yoga)`
- `search_by_dosha(dosha)`
- `hybrid_search(query, filters)`
- `search_by_citation(book_id)`

## Architecture

```text
File Upload
    ↓
Extractor (PDF / Markdown / TXT / OCR)
    ↓
Language Detector
    ↓
Translator (optional)
    ↓
Semantic Chunker
    ↓
Embedding Provider
    ↓
Vector Store (ChromaDB)
    ↓
Document Retrieval Engine
    ↓
Reasoning Engine / LLM
```

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

pipeline.process(
    "knowledge-base/books/Book PDFs/book.pdf",
    book_id="BPHS",
    book_title="Brihat Parashara Hora Shastra",
)

engine = DocumentRetrievalEngine(pipeline.vector_store, pipeline.embedder)
results = engine.semantic_search("marriage and 7th house")
for r in results:
    print(r.chunk.text, r.chunk.citation)
```

## Future Fine-Tuning

The chunk store can export training examples:

```text
Chunk
    ↓
Question / Prompt
    ↓
Context
    ↓
Answer
    ↓
Citation
```

This dataset can be used for supervised fine-tuning of the LLM.

## Primary Knowledge Source

Documents processed by this pipeline become the primary source of truth. The AI prioritizes retrieved chunks over general model knowledge and cites the relevant source whenever possible.
