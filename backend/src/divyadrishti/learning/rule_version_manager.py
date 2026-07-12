"""Rule Version Manager for knowledge versioning and admin review."""

import uuid
from datetime import datetime, timezone
from typing import Any

from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.knowledge.models import Rule


class RuleVersionManager:
    """Manage rule versions, proposals, approvals, and deprecations."""

    def __init__(self, repository: KnowledgeRepository) -> None:
        self.repository = repository
        self.pending_rules: list[Rule] = []

    def propose_rule(self, rule: Rule, proposed_by: str = "admin") -> Rule:
        """Propose a new rule for admin review."""
        rule.approval_status = "pending"
        rule.enabled = False
        rule.modified_by = proposed_by
        rule.modified_at = self._now()
        rule.change_history.append({"action": "proposed", "by": proposed_by, "at": rule.modified_at})
        self.pending_rules.append(rule)
        return rule

    def approve_rule(self, rule_id: str, approved_by: str = "admin") -> Rule:
        """Approve a proposed rule and add it to the repository."""
        for rule in self.pending_rules:
            if rule.rule_id == rule_id:
                rule.approval_status = "approved"
                rule.enabled = True
                rule.modified_by = approved_by
                rule.modified_at = self._now()
                rule.change_history.append({"action": "approved", "by": approved_by, "at": rule.modified_at})
                self.repository.add_rule(rule)
                self.pending_rules = [r for r in self.pending_rules if r.rule_id != rule_id]
                return rule

        existing = self.repository.get_rule(rule_id)
        if existing:
            existing.approval_status = "approved"
            existing.enabled = True
            existing.modified_by = approved_by
            existing.modified_at = self._now()
            existing.change_history.append({"action": "approved", "by": approved_by, "at": existing.modified_at})
            self.repository.update_rule(existing)
            return existing

        raise ValueError(f"Rule not found: {rule_id}")

    def reject_rule(self, rule_id: str, approved_by: str = "admin", reason: str = "") -> Rule:
        """Reject a proposed rule."""
        for rule in self.pending_rules:
            if rule.rule_id == rule_id:
                rule.approval_status = "rejected"
                rule.enabled = False
                rule.modified_by = approved_by
                rule.modified_at = self._now()
                rule.change_history.append({"action": "rejected", "by": approved_by, "at": rule.modified_at, "reason": reason})
                return rule
        raise ValueError(f"Rule not found: {rule_id}")

    def deprecate_rule(self, rule_id: str, deprecated_by: str = "admin", reason: str = "") -> Rule:
        """Mark a rule as deprecated without deleting it."""
        rule = self.repository.get_rule(rule_id)
        if not rule:
            raise ValueError(f"Rule not found: {rule_id}")

        rule.deprecated = True
        rule.enabled = False
        rule.approval_status = "deprecated"
        rule.modified_by = deprecated_by
        rule.modified_at = self._now()
        rule.change_history.append({"action": "deprecated", "by": deprecated_by, "at": rule.modified_at, "reason": reason})
        self.repository.update_rule(rule)
        return rule

    def update_rule(self, rule: Rule, updated_by: str = "admin") -> Rule:
        """Update a rule and create a new version entry."""
        existing = self.repository.get_rule(rule.rule_id)
        if not existing:
            raise ValueError(f"Rule not found: {rule.rule_id}")

        version_parts = existing.version.split(".")
        if len(version_parts) >= 3 and version_parts[2].isdigit():
            version_parts[2] = str(int(version_parts[2]) + 1)
        rule.version = ".".join(version_parts)
        rule.modified_by = updated_by
        rule.modified_at = self._now()
        rule.change_history = existing.change_history + [
            {"action": "updated", "by": updated_by, "at": rule.modified_at}
        ]
        self.repository.update_rule(rule)
        return rule

    def merge_duplicates(self, keep_id: str, duplicate_ids: list[str], merged_by: str = "admin") -> Rule:
        """Merge duplicate rules into one rule and deprecate the duplicates."""
        keep = self.repository.get_rule(keep_id)
        if not keep:
            raise ValueError(f"Rule not found: {keep_id}")

        for dup_id in duplicate_ids:
            self.deprecate_rule(dup_id, merged_by, f"Merged into {keep_id}")

        keep.interpretation += f" [Merged: {', '.join(duplicate_ids)}]"
        keep.modified_by = merged_by
        keep.modified_at = self._now()
        keep.change_history.append({"action": "merged", "by": merged_by, "at": keep.modified_at, "merged": duplicate_ids})
        self.repository.update_rule(keep)
        return keep

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
