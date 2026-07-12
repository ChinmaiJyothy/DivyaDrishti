# Knowledge Base Architecture

## Overview

DivyaDrishti's knowledge base is a structured, machine-readable repository of Vedic astrology rules derived from classical texts. The LLM does not invent astrology; it explains the reasoning produced from this knowledge base.

## Directory Structure

```text
knowledge-base/
├── books/          # Classical text metadata and chapter maps
│   ├── BPHS/
│   ├── Brihat_Jataka/
│   ├── Phaladeepika/
│   ├── Saravali/
│   ├── Jataka_Parijata/
│   ├── Laghu_Parashari/
│   ├── Hora_Sara/
│   └── Uttara_Kalamrita/
├── rules/          # Machine-readable rules by category
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
│   ├── spirituality/
│   └── classical-texts/
└── README.md
```

## Rule Schema

Every rule is a YAML or JSON object with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| rule_id | str | Yes | Unique uppercase ID, e.g. `BPHS_7TH_001` |
| source_book | str | Yes | Book ID or full title from `VALID_BOOKS` |
| chapter | str | No | Chapter or section reference |
| verse | str | No | Verse number |
| topic | str | Yes | High-level topic, e.g. `Marriage` |
| subtopic | str | No | More specific subtopic |
| category | str | Yes | Category folder, e.g. `marriage` |
| conditions | list[str] | Yes | Astrological conditions |
| astrological_factors | object | Yes | Structured factors (houses, planets, signs, etc.) |
| interpretation | str | Yes | The meaning when conditions are met |
| supporting_notes | str | No | Scholarly notes or caveats |
| confidence | float | Yes | Value between 0 and 1 |
| references | list[str] | No | Additional references |
| tags | list[str] | No | Search tags |
| enabled | bool | No | Whether the rule is active |

### astrological_factors Object

```yaml
astrological_factors:
  houses: [7]
  planets: [Jupiter]
  signs: [Libra]
  nakshatras: [Revati]
  yogas: [Raja Yoga]
  doshas: [Mangal Dosha]
  dashas: [Vimshottari]
  topics: [marriage]
```

## Import Pipeline

The `KnowledgeIngestionPipeline` supports:

- **YAML** (`.yaml`, `.yml`)
- **JSON** (`.json`)
- **Markdown** (`.md`) with YAML frontmatter

For Markdown, frontmatter may contain either `rules` (a list of rules) or `rule_id` (single rule). The body text becomes the `interpretation` if not already provided.

Future extensions:

- `parsers/pdf_parser.py` for PDF extraction
- `parsers/ocr_parser.py` for scanned manuscripts
- `parsers/annotation_parser.py` for manual scholar annotations

## Validation Pipeline

`RuleValidator` checks every imported rule:

- Schema validation via Pydantic
- Duplicate rule IDs within a batch
- Valid planet names
- Valid house numbers (1-12)
- Valid sign names
- Valid nakshatra names
- Valid yoga, dosha, and dasha values
- Confidence between 0 and 1
- Non-empty conditions and interpretation
- Known source book

## Retrieval Engine

`KnowledgeRetrievalEngine` supports:

- `retrieve_by_topic(topic)`
- `retrieve_by_house(house)`
- `retrieve_by_planet(planet)`
- `retrieve_by_sign(sign)`
- `retrieve_by_nakshatra(nakshatra)`
- `retrieve_by_yoga(yoga)`
- `retrieve_by_dosha(dosha)`
- `retrieve_by_dasha(dasha)`
- `retrieve_by_chapter(chapter)`
- `retrieve_by_source(source_book)`
- `retrieve_by_combination(factors)`
- `retrieve_by_query(query)`

The Reasoning Engine receives structured rules, not raw books.

## Citation System

Every rule exposes a `citation()` method returning:

```json
{
  "rule_id": "BPHS_7TH_001",
  "source_book": "BPHS",
  "chapter": "16",
  "verse": "1",
  "references": ["BPHS Chapter 16"]
}
```

The AI layer will cite these references naturally.

## Future Fine-Tuning Pipeline

The `TrainingDatasetExporter` generates JSONL examples with:

- `birth_chart`
- `question`
- `relevant_rules`
- `reasoning_steps`
- `final_answer`
- `source_references`

This can later be exported for supervised fine-tuning of an LLM on Vedic astrology reasoning.

## Example Rule

```yaml
- rule_id: BPHS_7TH_001
  source_book: BPHS
  chapter: "16"
  verse: "1"
  topic: Marriage
  category: marriage
  conditions:
    - Jupiter is strong in the 7th house or aspects the 7th lord
  astrological_factors:
    houses: [7]
    planets: [Jupiter]
    topics: [marriage]
  interpretation: A strong Jupiter influencing the 7th house supports a harmonious marriage.
  confidence: 0.85
  references:
    - BPHS Chapter 16
  tags:
    - marriage
    - jupiter
```

## Usage

```python
from divyadrishti.knowledge import KnowledgeRepository, KnowledgeRetrievalEngine

repo = KnowledgeRepository("knowledge-base")
repo.load()

engine = KnowledgeRetrievalEngine(repo)
rules = engine.retrieve_by_combination({"houses": [7], "planets": ["Jupiter"]})
for rule in rules:
    print(rule.interpretation, rule.citation())
```
