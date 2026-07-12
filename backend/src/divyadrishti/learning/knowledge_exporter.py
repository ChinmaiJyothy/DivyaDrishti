"""Knowledge Exporter for JSON, CSV, and YAML exports."""

import csv
import json
from pathlib import Path
from typing import Any

import yaml

from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.learning.feedback_manager import FeedbackManager
from divyadrishti.learning.models import AuditEntry


class KnowledgeExporter:
    """Export knowledge base, feedback, metrics, audit logs, and reasoning stats."""

    def __init__(
        self,
        repository: KnowledgeRepository,
        feedback: FeedbackManager | None = None,
    ) -> None:
        self.repository = repository
        self.feedback = feedback

    def export_knowledge_base(self, output_path: Path | str, format: str = "json") -> None:
        """Export all rules to the requested format."""
        output_path = Path(output_path)
        data = [rule.model_dump() for rule in self.repository.list_rules(enabled_only=False)]

        if format == "json":
            output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        elif format == "yaml":
            output_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, indent=2), encoding="utf-8")
        elif format == "csv":
            self._to_csv(data, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def export_feedback(self, output_path: Path | str, format: str = "json") -> None:
        """Export feedback to the requested format."""
        if not self.feedback:
            raise ValueError("Feedback manager not configured.")
        data = self.feedback.export()
        self._write(data, output_path, format)

    def export_metrics(self, metrics: list[Any], output_path: Path | str, format: str = "json") -> None:
        """Export quality metrics to the requested format."""
        data = [m.model_dump() for m in metrics]
        self._write(data, output_path, format)

    def export_audit_logs(self, logs: list[AuditEntry], output_path: Path | str, format: str = "json") -> None:
        """Export audit logs to the requested format."""
        data = [log.model_dump() for log in logs]
        self._write(data, output_path, format)

    def _write(self, data: list[dict], output_path: Path | str, format: str) -> None:
        output_path = Path(output_path)
        if format == "json":
            output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        elif format == "yaml":
            output_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, indent=2), encoding="utf-8")
        elif format == "csv":
            self._to_csv(data, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _to_csv(self, data: list[dict], output_path: Path) -> None:
        if not data:
            output_path.write_text("", encoding="utf-8")
            return

        fieldnames = list(data[0].keys())
        with output_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
