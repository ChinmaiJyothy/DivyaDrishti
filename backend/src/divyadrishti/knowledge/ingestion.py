"""Ingestion pipeline for importing knowledge from Markdown, JSON, and YAML."""

import json
from pathlib import Path
from typing import Any

import yaml

from divyadrishti.knowledge.exceptions import IngestionError
from divyadrishti.knowledge.models import Rule
from divyadrishti.knowledge.validation import RuleValidator


class KnowledgeIngestionPipeline:
    """Import knowledge rules from various file formats."""

    SUPPORTED_EXTENSIONS = {".yaml", ".yml", ".json", ".md"}

    def __init__(self, validator: RuleValidator | None = None) -> None:
        self.validator = validator or RuleValidator()

    def ingest_file(self, path: Path | str) -> list[Rule]:
        """Ingest a single file and return validated rules."""
        file_path = Path(path)
        if not file_path.exists():
            raise IngestionError(f"File not found: {file_path}")

        extension = file_path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise IngestionError(
                f"Unsupported file format '{extension}'. Supported: {self.SUPPORTED_EXTENSIONS}"
            )

        raw_content = file_path.read_text(encoding="utf-8")
        data = self._parse_content(raw_content, extension)

        if not isinstance(data, list):
            data = [data]

        validated: list[Rule] = []
        for item in data:
            if item is None:
                continue
            if not isinstance(item, dict):
                raise IngestionError(
                    f"Each rule must be a JSON/YAML object. Got: {type(item).__name__}"
                )
            validated.append(self.validator.validate(item))

        return validated

    def ingest_directory(self, directory: Path | str) -> list[Rule]:
        """Ingest all supported files in a directory recursively."""
        directory = Path(directory)
        if not directory.is_dir():
            raise IngestionError(f"Directory not found: {directory}")

        results: list[Rule] = []
        for path in sorted(directory.rglob("*")):
            if path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                results.extend(self.ingest_file(path))
        return results

    def ingest_book_chapters(self, book_file: Path | str) -> dict[str, str]:
        """Ingest a book metadata file and return chapter map."""
        file_path = Path(book_file)
        raw_content = file_path.read_text(encoding="utf-8")
        data = self._parse_content(raw_content, file_path.suffix.lower())
        if not isinstance(data, dict):
            raise IngestionError("Book metadata must be a single object.")
        return data.get("chapters", {})

    def _parse_content(self, content: str, extension: str) -> Any:
        if extension in {".yaml", ".yml"}:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as exc:
                raise IngestionError(f"Invalid YAML: {exc}") from exc

        if extension == ".json":
            try:
                return json.loads(content)
            except json.JSONDecodeError as exc:
                raise IngestionError(f"Invalid JSON: {exc}") from exc

        if extension == ".md":
            return self._parse_markdown(content)

        raise IngestionError(f"Unsupported extension: {extension}")

    def _parse_markdown(self, content: str) -> list[dict[str, Any]]:
        """Parse Markdown with YAML frontmatter and optional rule list."""
        content = content.strip()
        if not content.startswith("---"):
            raise IngestionError(
                "Markdown knowledge files must begin with YAML frontmatter."
            )

        parts = content.split("---", 2)
        if len(parts) < 3:
            raise IngestionError(
                "Markdown frontmatter must be enclosed by '---' delimiters."
            )

        frontmatter = parts[1].strip()
        body = parts[2].strip()

        try:
            meta = yaml.safe_load(frontmatter) or {}
        except yaml.YAMLError as exc:
            raise IngestionError(f"Invalid YAML frontmatter: {exc}") from exc

        if not isinstance(meta, dict):
            raise IngestionError("YAML frontmatter must be a mapping.")

        if "rules" in meta:
            rules = meta["rules"]
            if not isinstance(rules, list):
                raise IngestionError("The 'rules' frontmatter key must be a list.")
            return rules

        if "rule_id" in meta:
            if "interpretation" not in meta:
                meta["interpretation"] = body
            return [meta]

        raise IngestionError(
            "Markdown frontmatter must contain 'rules' or 'rule_id' and 'interpretation'."
        )
