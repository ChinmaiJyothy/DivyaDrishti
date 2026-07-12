# Continuous Learning & Improvement System

## Overview

The Adaptive Knowledge Learning system lets DivyaDrishti improve over time without retraining the language model. It learns from user feedback, admin corrections, and newly added books while preserving the integrity of the classical knowledge base.

## Principles

- Never modify original classical texts.
- Never automatically activate new knowledge.
- All changes are transparent, reviewable, and reversible.
- Every rule is versioned and audited.

## Components

### FeedbackManager

Collects user feedback on AI responses.

- Ratings: `Very Helpful`, `Helpful`, `Neutral`, `Not Helpful`, `Incorrect`
- Optional comments
- Links feedback to conversation, question, reasoning trace, rules used, and generated response

### RuleVersionManager

Manages rule lifecycle:

- `propose_rule` — creates a pending rule
- `approve_rule` — activates a pending rule
- `reject_rule` — rejects a pending rule
- `deprecate_rule` — marks a rule as deprecated without deletion
- `update_rule` — creates a new version of an existing rule
- `merge_duplicates` — merges duplicate rules and deprecates duplicates

Every rule includes:

- `version`
- `created_at` / `modified_at`
- `modified_by`
- `approval_status`
- `change_history`
- `deprecated` flag

### QualityAnalyzer

Computes rule quality scores from:

- Usage frequency
- Positive feedback
- Negative feedback
- Conflict frequency
- Retrieval frequency
- Confidence stability

### ConflictAnalyzer

Detects:

- Duplicate rules (same factors, similar interpretation)
- Conflicting rules (same factors, opposite interpretation)

### BookImportMonitor

Processes new books through the Document Pipeline and generates an `IngestionReport`:

- Candidate rules
- Duplicate detection
- Conflict detection
- New topics
- Missing metadata
- Incomplete references

New rules are created with `approval_status=pending` and `enabled=False`.

### KnowledgeAnalytics

Provides:

- Most used books
- Most referenced chapters
- Most common topics
- Knowledge coverage
- Unused rules
- Frequently conflicting rules
- Most trusted rules

### AuditLogger

Tracks every important action:

- `RULE_CREATED`
- `RULE_UPDATED`
- `RULE_APPROVED`
- `RULE_REJECTED`
- `RULE_DEPRECATED`
- `RULE_MERGED`
- `BOOK_IMPORTED`
- `FEEDBACK_RECEIVED`
- `ADMIN_DECISION`

Each entry includes timestamp, user, reason, affected objects, and metadata.

### KnowledgeExporter

Exports to:

- JSON
- CSV
- YAML

Exportable items:

- Knowledge base
- Feedback
- Rule quality metrics
- Audit logs
- Training dataset
- Reasoning statistics

## Learning Pipeline

```text
User Feedback / Admin Correction / New Book
    ↓
FeedbackManager / RuleVersionManager / BookImportMonitor
    ↓
QualityAnalyzer / ConflictAnalyzer / KnowledgeAnalytics
    ↓
Admin Review
    ↓
RuleVersionManager approve / reject / deprecate
    ↓
AuditLogger
    ↓
Knowledge Base Updated
```

## Safety

- Original books remain untouched.
- New rules are never active until approved.
- Deprecated rules are preserved for history.
- All changes are logged.
