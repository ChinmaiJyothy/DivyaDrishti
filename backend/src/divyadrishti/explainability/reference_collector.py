"""Reference Collector for the Explainability Engine."""

from divyadrishti.explainability.models import ReferenceEntry, SuggestedReading
from divyadrishti.knowledge import KnowledgeRepository
from divyadrishti.reasoning.models import Evidence


class ReferenceCollector:
    """Collect classical references from rules and evidence."""

    def __init__(self, repository: KnowledgeRepository | None = None) -> None:
        self.repository = repository

    def collect(self, evidence_list: list[Evidence]) -> list[ReferenceEntry]:
        """Collect structured references from a list of evidence."""
        references: list[ReferenceEntry] = []
        seen: set[str] = set()

        for ev in evidence_list:
            rule = self.repository.get_rule(ev.rule_id) if self.repository else None

            if rule:
                key = f"{rule.rule_id}-{rule.chapter}-{rule.verse}"
                if key in seen:
                    continue
                seen.add(key)

                book = self.repository.get_book(rule.source_book) if self.repository else None
                chapter_title = None
                if book and rule.chapter and rule.chapter in book.chapters:
                    chapter_title = book.chapters[rule.chapter]

                references.append(
                    ReferenceEntry(
                        book=book.title if book else rule.source_book,
                        chapter=chapter_title or rule.chapter,
                        verse=rule.verse,
                        page=None,
                        original_language=book.language if book else None,
                        translated_text=rule.interpretation,
                    )
                )

        return references

    def suggest_reading(self, domain: str, evidence_list: list[Evidence]) -> list[SuggestedReading]:
        """Suggest relevant classical chapters based on evidence."""
        suggestions: list[SuggestedReading] = []
        seen: set[str] = set()

        for ev in evidence_list:
            rule = self.repository.get_rule(ev.rule_id) if self.repository else None
            if not rule:
                continue

            key = f"{rule.source_book}-{rule.chapter}"
            if key in seen:
                continue
            seen.add(key)

            book = self.repository.get_book(rule.source_book) if self.repository else None
            suggestions.append(
                SuggestedReading(
                    book=book.title if book else rule.source_book,
                    chapter=rule.chapter,
                    topic=domain,
                )
            )

        return suggestions
