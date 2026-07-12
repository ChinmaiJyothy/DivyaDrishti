# Evidence & Rule Evaluation Engine

This package is the core intelligence of DivyaDrishti. It evaluates Vedic astrology rules against a birth chart and produces a structured `ReasoningTrace` for the LLM layer.

## Pipeline

```text
Birth Chart
    ↓
Knowledge Retrieval
    ↓
Evidence & Rule Evaluation Engine
    ↓
Structured Reasoning
    ↓
LLM Conversation Engine
```

## Components

- `engine.py` — `EvidenceEngine` public API
- `evaluator.py` — `RuleEvaluator` evaluates single rules against a chart
- `scoring.py` — matching logic, confidence, and weight computation
- `aggregator.py` — `EvidenceAggregator` combines evidence and detects conflicts
- `conflict.py` — conflict detection between evidence
- `sentiment.py` — lightweight deterministic sentiment analysis
- `models.py` — `ChartData`, `PlanetPosition`, `Evidence`, `ReasoningTrace`

## Usage

```python
from divyadrishti.knowledge import KnowledgeRepository, KnowledgeRetrievalEngine
from divyadrishti.reasoning import EvidenceEngine

repo = KnowledgeRepository("knowledge-base")
repo.load()

retriever = KnowledgeRetrievalEngine(repo)
rules = retriever.retrieve_by_combination({"houses": [7], "planets": ["Jupiter"]})

chart = {
    "planets": {
        "Jupiter": {"house": 7, "sign": "Libra"},
    },
    "yogas": ["Gaja Kesari Yoga"],
    "doshas": [],
}

engine = EvidenceEngine()
trace = engine.evaluate(chart, "Will I have a happy marriage?", rules)
print(trace.reasoning_summary)
```

## Output

The final `ReasoningTrace` contains:

- `question`
- `chart_data`
- `matched_rules` (all evaluated evidence)
- `supporting_evidence`
- `conflicting_evidence`
- `overall_confidence` (0-100)
- `reasoning_summary`

## No LLM

This engine does not use an LLM. All reasoning is deterministic and based on the structured knowledge base.
