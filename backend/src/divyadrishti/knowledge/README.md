# Knowledge Acquisition Framework

This package manages the structured Vedic astrology knowledge base for DivyaDrishti.

## Purpose

- Ingest rules from classical texts (Markdown, JSON, YAML).
- Validate rules against schema and Vedic astrology domain constraints.
- Store rules in a file-based repository.
- Retrieve relevant rules for chart interpretation.
- Generate citations for every interpretation.
- Export supervised fine-tuning datasets.

## Architecture

```text
knowledge/
├── models.py        # Pydantic models: Rule, Book, Citation, ReasoningInput, TrainingEntry
├── constants.py     # Valid planets, houses, nakshatras, signs, books, etc.
├── validation.py    # RuleValidator: schema and domain validation
├── ingestion.py     # KnowledgeIngestionPipeline: Markdown, JSON, YAML import
├── repository.py    # KnowledgeRepository: file-based storage and loading
├── retrieval.py     # KnowledgeRetrievalEngine: query and filter rules
├── dataset.py       # TrainingDatasetExporter: future fine-tuning dataset export
└── exceptions.py    # KnowledgeError hierarchy
```

## Usage

```python
from divyadrishti.knowledge import KnowledgeRepository, KnowledgeRetrievalEngine

repo = KnowledgeRepository("knowledge-base")
repo.load()

engine = KnowledgeRetrievalEngine(repo)
rules = engine.retrieve_by_combination({"houses": [7], "planets": ["Jupiter"]})
```

## Rule Schema

See `docs/KNOWLEDGE_BASE.md` for the full rule schema and example rules.

## Future Extensibility

- PDF extraction: add `parsers/pdf_parser.py` returning frontmatter-like dicts.
- OCR: add `parsers/ocr_parser.py` over scanned manuscript images.
- Search: replace in-memory retrieval with a vector/text index (e.g., Elasticsearch, SQLite FTS).
- Annotations: add a review workflow to attach scholar annotations to rules.
