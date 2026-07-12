"""File-based repository for Vedic astrology knowledge."""

import json
from pathlib import Path

import yaml

from divyadrishti.knowledge.constants import DEFAULT_RULE_CATEGORIES
from divyadrishti.knowledge.exceptions import IngestionError
from divyadrishti.knowledge.ingestion import KnowledgeIngestionPipeline
from divyadrishti.knowledge.models import Book, Rule
from divyadrishti.knowledge.validation import RuleValidator


class KnowledgeRepository:
    """Load and store knowledge rules and book metadata from the file system."""

    def __init__(
        self,
        base_path: Path | str,
        validator: RuleValidator | None = None,
    ) -> None:
        self.base_path = Path(base_path)
        self.rules_path = self.base_path / "rules"
        self.books_path = self.base_path / "books"
        self.validator = validator or RuleValidator()
        self.ingestion = KnowledgeIngestionPipeline(self.validator)
        self.rules: list[Rule] = []
        self.books: dict[str, Book] = {}

    def load(self) -> None:
        """Load all rules and books from the knowledge base directory."""
        self.rules = []
        self.books = {}
        self._load_rules()
        self._load_books()

    def _load_rules(self) -> None:
        if not self.rules_path.exists():
            return

        for category_dir in sorted(self.rules_path.iterdir()):
            if not category_dir.is_dir():
                continue
            for file in sorted(category_dir.iterdir()):
                if file.suffix.lower() in {".yaml", ".yml", ".json"}:
                    self.rules.extend(self.ingestion.ingest_file(file))

    def _load_books(self) -> None:
        if not self.books_path.exists():
            return

        for book_dir in sorted(self.books_path.iterdir()):
            if not book_dir.is_dir():
                continue
            book_file = book_dir / "book.yaml"
            if book_file.exists():
                content = book_file.read_text(encoding="utf-8")
                data = yaml.safe_load(content)
                if isinstance(data, dict):
                    book = Book.model_validate(data)
                    self.books[book.book_id] = book

    def get_rule(self, rule_id: str) -> Rule | None:
        """Retrieve a rule by its unique ID."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    def list_rules(self, enabled_only: bool = True) -> list[Rule]:
        """Return all loaded rules."""
        if enabled_only:
            return [rule for rule in self.rules if rule.enabled]
        return self.rules

    def add_rule(self, rule: Rule, save: bool = True) -> None:
        """Add a new rule to the repository and optionally persist it."""
        if self.get_rule(rule.rule_id):
            raise IngestionError(f"Rule {rule.rule_id} already exists.")
        self.rules.append(rule)
        if save:
            self._save_rule(rule)

    def _save_rule(self, rule: Rule) -> None:
        category_dir = self.rules_path / rule.category
        category_dir.mkdir(parents=True, exist_ok=True)
        file_path = category_dir / "rules.yaml"
        existing = []
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            if isinstance(data, list):
                existing = data
        existing.append(rule.model_dump(exclude_none=True))
        file_path.write_text(
            yaml.safe_dump(existing, sort_keys=False, allow_unicode=True, indent=2),
            encoding="utf-8",
        )

    def add_book(self, book: Book) -> None:
        """Add a book metadata entry."""
        self.books[book.book_id] = book

    def get_book(self, book_id: str) -> Book | None:
        """Retrieve a book by its ID."""
        return self.books.get(book_id)

    def list_books(self) -> list[Book]:
        """Return all loaded books."""
        return list(self.books.values())

    def export_rules(self, output_path: Path | str) -> None:
        """Export all rules as JSON."""
        output_path = Path(output_path)
        data = [rule.model_dump() for rule in self.rules]
        output_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
