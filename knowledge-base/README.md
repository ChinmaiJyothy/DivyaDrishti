# DivyaDrishti Knowledge Base

This directory contains the structured, machine-readable Vedic astrology knowledge base.

## Structure

```text
knowledge-base/
├── books/          # Classical text metadata and chapter/verse references
│   ├── BPHS/
│   ├── Brihat_Jataka/
│   ├── Phaladeepika/
│   └── ...
├── rules/          # Machine-readable rules derived from the books
│   ├── houses/
│   ├── planets/
│   ├── nakshatras/
│   ├── dashas/
│   ├── transits/
│   ├── yogas/
│   ├── doshas/
│   ├── career/
│   ├── marriage/
│   ├── finance/
│   ├── health/
│   ├── relationships/
│   └── spirituality/
└── schema/         # JSON schema for rule validation (optional)
```

## Rule Files

Each rule file is YAML or JSON and contains a list of rules. Rules must follow the schema documented in `docs/KNOWLEDGE_BASE.md`.

## Books

Book metadata is stored in `books/<book-id>/book.yaml`. Chapters and verses can be referenced inside `chapters/` or directly in `book.yaml`.

## Adding Knowledge

1. Add a rule file under `rules/<category>/`.
2. Validate rule IDs are unique.
3. Reference the book, chapter, and verse.
4. Run the validation pipeline.
