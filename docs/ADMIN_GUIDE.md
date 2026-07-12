# Administrator Guide

## Knowledge Lifecycle

1. **Import** — A new book or rule is imported.
2. **Review** — Admin reviews the `IngestionReport`, `QualityMetrics`, and `ConflictAnalyzer` output.
3. **Approve / Reject / Deprecate** — Admin changes `approval_status`.
4. **Version** — `RuleVersionManager` increments the rule version and appends to `change_history`.
5. **Audit** — `AuditLogger` records the action.
6. **Export** — Knowledge base, audit logs, and metrics can be exported for backup.

## Rule Approval Workflow

```python
from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.learning import RuleVersionManager, AuditLogger, AuditAction

repo = KnowledgeRepository("knowledge-base")
repo.load()

versions = RuleVersionManager(repo)
audit = AuditLogger()

# Review pending rule
pending = versions.pending_rules[0]

# Approve
versions.approve_rule(pending.rule_id, approved_by="admin")

# Log
audit.log(AuditAction.RULE_APPROVED, user="admin", reason="Verified", affected_objects=[pending.rule_id])
```

## Handling Conflicts

```python
from divyadrishti.learning import ConflictAnalyzer

analyzer = ConflictAnalyzer(repo)
duplicates = analyzer.find_duplicates()
conflicts = analyzer.find_conflicts()

# Merge duplicates
versions.merge_duplicates("BPHS_7TH_001", ["BPHS_7TH_002"], merged_by="admin")
```

## Book Ingestion

```python
from divyadrishti.learning import BookImportMonitor

monitor = BookImportMonitor(repo)
report = monitor.process("new_book.pdf", "NEW_BOOK", "New Book Title")

# Review report
for finding in report.findings:
    print(finding.type, finding.message)

# Candidate rules are pending and not active
for rule in report.candidate_rules:
    print(rule.rule_id, rule.approval_status)
```

## Analytics

```python
from divyadrishti.learning import KnowledgeAnalytics

analytics = KnowledgeAnalytics(repo)
print(analytics.knowledge_coverage())
print(analytics.most_used_books())
print(analytics.most_trusted_rules())
```

## Export

```python
from divyadrishti.learning import KnowledgeExporter

exporter = KnowledgeExporter(repo)
exporter.export_knowledge_base("kb.json", "json")
exporter.export_knowledge_base("kb.csv", "csv")
```

## Best Practices

- Never approve a rule without checking its source and factors.
- Deprecate rather than delete rules.
- Resolve conflicts before approving.
- Review feedback weekly.
- Export audit logs before bulk operations.
