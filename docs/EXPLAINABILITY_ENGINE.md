# Explainability Engine (XAI)

## Overview

The Explainable Astrology Engine converts the structured `ReasoningResult` into a transparent, human-understandable `ExplainabilityReport`. It is a deterministic, rule-based layer with no LLM involvement. The report is designed to power the frontend's "Why?" section.

## Principles

- Every astrological conclusion must be traceable.
- No unexplained predictions.
- No LLM is used.
- No natural language responses are generated.
- Output is structured data only.

## Input

The engine receives:

- Birth chart (`AstrologicalChart`)
- User question
- `ReasoningResult`
- `Evidence` objects
- Matched, partially matched, and ignored rules
- Confidence score
- Classical references

## Output

The `ExplainabilityReport` contains:

- `question` — original user question
- `detected_domain` — e.g., marriage, career, health
- `chart_factors_used` — planets, houses, signs, dashas, etc.
- `rules_considered` — all rule IDs evaluated
- `matched_rules` — `RuleTrace` objects for matched rules
- `ignored_rules` — `RuleTrace` objects for partially matched and unmatched rules
- `supporting_evidence` — explanations of supporting factors
- `conflicting_evidence` — explanations of conflicting factors
- `reasoning_path` — traversable reasoning graph
- `confidence_score` — overall confidence with contributor breakdown
- `limitations` — known limitations of the interpretation
- `classical_references` — structured classical citations
- `suggested_reading` — relevant classical chapters
- `important_notes` — safety and interpretation notes
- `visualizations` — frontend-ready visualization data

## Components

### ExplainabilityEngine

The main orchestrator. Calls each component and assembles the final report.

### ReasoningGraphBuilder

Builds a traversable reasoning graph:

```text
Question
  ↓
Detect Domain
  ↓
Retrieve Relevant Rules
  ↓
Evaluate Chart Factors
  ↓
Combine Evidence
  ↓
Conclusion
```

Each factor (houses, planets, signs, nakshatras, yogas, doshas, dashas, topics) is a child node.

### RuleTracer

Produces a `RuleTrace` for each piece of evidence:

- `rule_id`
- `source_book`
- `chapter` / `verse`
- `conditions` and `matched_conditions`
- `weight` and `confidence`
- `reason_included` or `reason_excluded`

### EvidenceExplainer

Explains why each factor matters and which rule/source caused it. For conflicts, it explains the confidence reduction.

### ConfidenceExplainer

Breaks down the overall confidence into individual `ConfidenceContribution` entries:

- `+ Strong Jupiter` (support)
- `- Saturn Delay` (conflict)

### ReferenceCollector

Collects `ReferenceEntry` objects from the knowledge base:

- Book
- Chapter
- Verse
- Page
- Original language
- Translated text

It never fabricates references.

### VisualizationBuilder

Generates frontend-ready data structures:

- `decision_tree`
- `reasoning_timeline`
- `evidence_tree`
- `planet_influence_graph`
- `house_influence_graph`
- `knowledge_source_graph`

### ReportSerializer

Serializes `ExplainabilityReport` to JSON, YAML, or dict.

## Reasoning Graph Model

```python
class Node:
    id: str
    label: str
    type: str
    children: list[Node]
    metadata: dict

class ReasoningGraph:
    root: Node
```

## Confidence Breakdown Model

```python
class ConfidenceBreakdown:
    overall_confidence: float
    contributors: list[ConfidenceContribution]

class ConfidenceContribution:
    name: str
    contribution: float
    type: str  # "support" or "conflict"
```

## Rule Trace Model

```python
class RuleTrace:
    rule_id: str
    source_book: str
    chapter: str | None
    verse: str | None
    page: str | None
    conditions: list[str]
    matched_conditions: list[str]
    weight: float
    confidence: float
    match_status: str
    reason_included: str
    reason_excluded: str
```

## Usage

```python
from divyadrishti.explainability import ExplainabilityEngine
from divyadrishti.reasoning.astrological.models import ReasoningResult, AstrologicalChart

engine = ExplainabilityEngine(repository)
report = engine.explain(
    question="Will I have a happy marriage?",
    chart=chart,
    result=result,
)

print(report.model_dump_json(indent=2))
```

## Limitations

The engine automatically reports limitations such as:

- Low confidence
- Conflicting evidence
- Insufficient evidence
- Missing dasha timing
- Unknown birth time accuracy

## Safety

- No LLM is used.
- No fabricated references.
- No natural language responses.
- Classical references are sourced from the knowledge base.
