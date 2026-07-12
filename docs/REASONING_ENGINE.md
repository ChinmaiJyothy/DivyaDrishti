# Reasoning Engine Design

## Purpose

The Reasoning Engine turns a structured birth chart and a user question into a `ReasoningTrace` that the LLM can explain. It does not generate predictions itself. It only evaluates evidence from the knowledge base.

## Architecture

The Reasoning Engine is split into two layers:

1. **Evidence & Rule Evaluation Engine** — evaluates individual rules against the chart.
2. **Reasoning Engine** (future) — consumes the `ReasoningTrace` and may enrich it with timing, dasha, and chart synthesis.

```text
Birth Chart
    ↓
Knowledge Retrieval
    ↓
Evidence & Rule Evaluation Engine
    ↓
ReasoningTrace
    ↓
LLM Conversation Engine
```

## Evidence & Rule Evaluation Engine

### RuleEvaluator

Evaluates a single `Rule` against a `ChartData`.

Steps:
- Match `astrological_factors` against the chart.
- Score the match.
- Build an `Evidence` object.

### Evidence

Fields:
- `rule_id`
- `source`
- `conditions`
- `matched_conditions`
- `confidence` (0-100)
- `weight`
- `supporting` (rule IDs)
- `conflicting` (rule IDs)
- `explanation`
- `notes`

### EvidenceAggregator

Responsibilities:
- Combine evidence from many rules.
- Remove duplicate rule IDs.
- Resolve conflicts using deterministic sentiment analysis.
- Normalize confidence.
- Rank strongest evidence.
- Generate `ReasoningTrace`.

### Conflict Detection

The engine detects conflicts by:
- Checking if evidence is about the same topic.
- Comparing the sentiment of each rule's interpretation.
- Marking opposite sentiments as conflicting.

This is deterministic and does not use an LLM.

### Confidence Algorithm

```text
confidence = rule.confidence * 100 * (1 + 0.1 * matched_factor_count)
weight = rule.confidence * matched_factor_count
overall_confidence = weighted average of supporting evidence - conflicting evidence
```

## ReasoningTrace Schema

```json
{
  "question": "Will I have a happy marriage?",
  "chart_data": {...},
  "matched_rules": [...],
  "supporting_evidence": [...],
  "conflicting_evidence": [...],
  "overall_confidence": 78.5,
  "reasoning_summary": "..."
}
```

## Example

```python
from divyadrishti.reasoning import EvidenceEngine

chart = {
    "planets": {
        "Jupiter": {"house": 7, "sign": "Libra"},
        "Saturn": {"house": 7, "sign": "Libra"},
    },
    "yogas": ["Gaja Kesari Yoga"],
    "doshas": ["Mangal Dosha"],
}

trace = engine.evaluate(chart, "Will I have a happy marriage?", rules)
```

## Extensibility

- Add `timing` evaluation using dasha and transit data.
- Replace keyword sentiment with a more nuanced model when the Astrology Engine is complete.
- Add `ReasoningEngine` layer that can synthesize multiple `ReasoningTrace` objects.
