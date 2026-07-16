"""Corpus repository."""

from sqlalchemy.orm import Session

from divyadrishti.models import Corpus


class CorpusRepository:
    """Database operations for knowledge corpora."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self, active_only: bool = True) -> list[Corpus]:
        query = self.db.query(Corpus)
        if active_only:
            query = query.filter(Corpus.is_active.is_(True))
        return query.order_by(Corpus.name.asc()).all()

    def get_by_id(self, corpus_id: int) -> Corpus | None:
        return self.db.query(Corpus).filter(Corpus.id == corpus_id).first()

    def get_by_slug(self, slug: str) -> Corpus | None:
        return self.db.query(Corpus).filter(Corpus.slug == slug).first()

    def create(self, corpus: Corpus) -> Corpus:
        self.db.add(corpus)
        self.db.commit()
        self.db.refresh(corpus)
        return corpus

    def get_or_create_default(self) -> Corpus:
        """Return the default 'Classical Vedic Astrology' corpus, creating it if missing.

        This preserves backward compatibility: books uploaded without an
        explicit corpus are attached to this default corpus.
        """
        default = self.get_by_slug("classical-vedic-astrology")
        if default:
            return default
        default = Corpus(
            slug="classical-vedic-astrology",
            name="Classical Vedic Astrology",
            corpus_type="classical",
            description="Default corpus for classical Parashari texts (backward-compatible with the file-based rule repository).",
        )
        return self.create(default)
