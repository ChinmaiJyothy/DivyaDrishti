# Reasoning Engine Design

## Purpose

The Reasoning Engine turns a structured birth chart and a user question into a `ReasoningTrace` that the LLM can explain. It does not generate predictions itself. It only evaluates evidence from the knowledge base.

## Architecture

The Reasoning Engine is split into two layers:

1. **Evidence & Rule Evaluation Engine** — evaluates individual rules against the chart.
2. **Astrological Reasoning Engine** — orchestrates question analysis, rule retrieval, evidence evaluation, conflict resolution, confidence calculation, and structured reasoning aggregation.

```text
Birth Chart + User Question
    ↓
QuestionAnalyzer
    ↓
RuleMatcher
    ↓
EvidenceEvaluator
    ↓
ConflictResolver
    ↓
ConfidenceCalculator
    ↓
ReasoningAggregator
    ↓
ReasoningSerializer
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

## Astrological Reasoning Engine

The Astrological Reasoning Engine emulates the analytical workflow of an experienced Vedic astrologer. It never generates natural language and never communicates with users.

### Components

- **QuestionAnalyzer** — determine the astrological domain and relevant entities.
- **RuleMatcher** — retrieve relevant rules from the knowledge base.
- **EvidenceEvaluator** — evaluate each rule against the chart.
- **ConflictResolver** — separate supporting and conflicting evidence.
- **ConfidenceCalculator** — compute overall confidence.
- **ReasoningAggregator** — build the final `ReasoningResult`.
- **ReasoningSerializer** — convert the result into a `ReasoningTrace`.

### Input

```python
ReasoningRequest(
    question="Will I have a happy marriage?",
    chart=AstrologicalChart(
        maha_dasha="Jupiter",
        antar_dasha="Saturn",
        planets={
            "Jupiter": {"house": 7, "sign": "Libra"},
            "Saturn": {"house": 7, "sign": "Libra"},
        },
        yogas=["Gaja Kesari"],
        doshas=["Manglik"],
    ),
)
```

### Output ReasoningResult

```json
{
  "question": "Will I have a happy marriage?",
  "domain": "marriage",
  "relevant_factors": {
    "houses": [7],
    "planets": ["Venus", "Jupiter"],
    "dashas": ["Jupiter", "Saturn"]
  },
  "matched_rules": [...],
  "partially_matched_rules": [...],
  "unmatched_rules": [...],
  "supporting_evidence": [...],
  "conflicting_evidence": [...],
  "overall_confidence": 78.5,
  "reasoning_summary": "Domain=marriage. Matched=2. Conflicting=1.",
  "reasoning_steps": [...],
  "suggested_follow_up_topics": ["Timing of marriage", "Spouse characteristics", "Marriage compatibility"]
}
```

## ReasoningTrace Schema

```json
{
  "question": "Will I have a happy marriage?",
  "domain": "marriage",
  "chart_data": {...},
  "relevant_factors": {...},
  "matched_rules": [...],
  "supporting_evidence": [...],
  "conflicting_evidence": [...],
  "overall_confidence": 78.5,
  "reasoning_summary": "...",
  "reasoning_steps": [...],
  "suggested_follow_up_topics": [...]
}
```

## Example

```python
from divyadrishti.reasoning import AstrologicalReasoningEngine
from divyadrishti.reasoning.astrological import ReasoningRequest, AstrologicalChart

engine = AstrologicalReasoningEngine(knowledge_engine)

request = ReasoningRequest(
    question="Will I have a happy marriage?",
    chart=AstrologicalChart(...),
)

result = engine.reason(request)
trace = engine.reason_trace(request)
```

## Extensibility

- Add `timing` evaluation using dasha and transit data.
- Replace keyword sentiment with a more nuanced model when the Astrology Engine is complete.
- Add `ReasoningEngine` layer that can synthesize multiple `ReasoningTrace` objects.
