"""Exceptions for the knowledge acquisition framework."""


class KnowledgeError(Exception):
    """Base exception for the knowledge subsystem."""


class RuleValidationError(KnowledgeError):
    """Raised when a rule fails validation."""

    def __init__(self, message: str, rule_id: str | None = None):
        super().__init__(message)
        self.rule_id = rule_id
        self.message = message

    def __str__(self) -> str:
        if self.rule_id:
            return f"Rule {self.rule_id}: {self.message}"
        return self.message


class DuplicateRuleError(KnowledgeError):
    """Raised when a rule ID is not unique."""

    def __init__(self, rule_id: str):
        self.rule_id = rule_id
        super().__init__(f"Duplicate rule ID: {rule_id}")


class IngestionError(KnowledgeError):
    """Raised when a knowledge source cannot be ingested."""


class RetrievalError(KnowledgeError):
    """Raised when a knowledge query fails."""


class CitationError(KnowledgeError):
    """Raised when a citation cannot be generated."""
