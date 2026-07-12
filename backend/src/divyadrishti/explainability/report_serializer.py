"""Report Serializer for the Explainability Engine."""

import json
from pathlib import Path
from typing import Any

import yaml

from divyadrishti.explainability.models import ExplainabilityReport


class ReportSerializer:
    """Serialize ExplainabilityReport to JSON, YAML, or dict."""

    def to_dict(self, report: ExplainabilityReport) -> dict[str, Any]:
        """Convert a report to a plain dictionary."""
        return report.model_dump()

    def to_json(self, report: ExplainabilityReport) -> str:
        """Serialize a report to JSON."""
        return json.dumps(report.model_dump(), indent=2, ensure_ascii=False)

    def to_yaml(self, report: ExplainabilityReport) -> str:
        """Serialize a report to YAML."""
        return yaml.safe_dump(report.model_dump(), sort_keys=False, allow_unicode=True, indent=2)

    def save_json(self, report: ExplainabilityReport, path: Path | str) -> None:
        """Save a report as JSON."""
        Path(path).write_text(self.to_json(report), encoding="utf-8")

    def save_yaml(self, report: ExplainabilityReport, path: Path | str) -> None:
        """Save a report as YAML."""
        Path(path).write_text(self.to_yaml(report), encoding="utf-8")
