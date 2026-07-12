"""Audit Logger for tracking knowledge and learning actions."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AuditAction:
    """Audit action constants."""

    RULE_CREATED = "RULE_CREATED"
    RULE_UPDATED = "RULE_UPDATED"
    RULE_APPROVED = "RULE_APPROVED"
    RULE_REJECTED = "RULE_REJECTED"
    RULE_DEPRECATED = "RULE_DEPRECATED"
    RULE_MERGED = "RULE_MERGED"
    BOOK_IMPORTED = "BOOK_IMPORTED"
    FEEDBACK_RECEIVED = "FEEDBACK_RECEIVED"
    ADMIN_DECISION = "ADMIN_DECISION"


class AuditEntry(BaseModel):
    """A single audit log entry."""

    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    action: str
    user: str
    reason: str
    affected_objects: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogger:
    """Record and query audit logs."""

    def __init__(self) -> None:
        self.logs: list[AuditEntry] = []

    def log(
        self,
        action: str,
        user: str = "system",
        reason: str = "",
        affected_objects: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Record an audit entry."""
        entry = AuditEntry(
            action=action,
            user=user,
            reason=reason,
            affected_objects=affected_objects or [],
            metadata=metadata or {},
        )
        self.logs.append(entry)
        return entry

    def for_object(self, object_id: str) -> list[AuditEntry]:
        """Return all audit entries affecting an object."""
        return [entry for entry in self.logs if object_id in entry.affected_objects]

    def export(self) -> list[dict[str, Any]]:
        """Export all audit logs."""
        return [entry.model_dump() for entry in self.logs]
