"""Rule extraction for the Knowledge Corpus.

This module scans processed document chunks for recognizable Vedic
astrology terminology (planets, houses, signs, nakshatras, yogas,
doshas, dashas) and condition-like phrasing, producing *candidate*
rules. Candidate rules are a heuristic, deterministic, rule-based
extraction — this is explicitly NOT a trained ML model and NEVER
becomes active knowledge until an administrator approves it.
"""

import re
import uuid
from typing import Any

from pydantic import BaseModel, Field

from divyadrishti.astrology.constants import PLANETS, SIGN_NAMES
from divyadrishti.documents.models import DocumentChunk
from divyadrishti.knowledge.constants import (
    TOPIC_KEYWORDS,
    VALID_DASHAS,
    VALID_DOSHAS,
    VALID_NAKSHATRAS,
    VALID_YOGAS,
)

_HOUSE_PATTERN = re.compile(r"(?i)\b(\d{1,2})(?:st|nd|rd|th)?\s+house\b|\bhouse\s+(\d{1,2})\b")

_CONDITION_MARKERS = (
    "if",
    "when",
    "gives",
    "give",
    "results in",
    "causes",
    "indicates",
    "yields",
    "denotes",
    "bestows",
    "confers",
    "produces",
)

MIN_TEXT_LENGTH = 25
MAX_TEXT_LENGTH_FOR_FULL_CONFIDENCE = 600


class DetectedFactors(BaseModel):
    """Astrological factors detected in a chunk of text."""

    houses: list[int] = Field(default_factory=list)
    planets: list[str] = Field(default_factory=list)
    signs: list[str] = Field(default_factory=list)
    nakshatras: list[str] = Field(default_factory=list)
    yogas: list[str] = Field(default_factory=list)
    doshas: list[str] = Field(default_factory=list)
    dashas: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)

    def is_empty(self) -> bool:
        return not any(
            [
                self.houses,
                self.planets,
                self.signs,
                self.nakshatras,
                self.yogas,
                self.doshas,
                self.dashas,
            ]
        )

    def factor_category_count(self) -> int:
        return sum(
            1
            for values in (
                self.houses,
                self.planets,
                self.signs,
                self.nakshatras,
                self.yogas,
                self.doshas,
                self.dashas,
            )
            if values
        )


class CandidateRuleDraft(BaseModel):
    """An in-memory candidate rule draft, prior to persistence for review."""

    candidate_rule_id: str = Field(default_factory=lambda: f"CAND_{uuid.uuid4().hex[:12].upper()}")
    chunk_id: str
    source_book_title: str
    language: str = "en"
    chapter: str | None = None
    verse: str | None = None
    page: int | None = None
    original_text: str
    translated_text: str | None = None
    topic: str = "general"
    subtopic: str | None = None
    astrological_factors: DetectedFactors = Field(default_factory=DetectedFactors)
    candidate_conditions: list[str] = Field(default_factory=list)
    candidate_interpretation: str
    confidence: float = 0.0


class AstrologicalFactorDetector:
    """Detect astrological entities mentioned in a piece of text."""

    def detect(self, text: str) -> DetectedFactors:
        lower = text.lower()

        houses: list[int] = []
        for match in _HOUSE_PATTERN.finditer(text):
            value = match.group(1) or match.group(2)
            if value:
                house_num = int(value)
                if 1 <= house_num <= 12 and house_num not in houses:
                    houses.append(house_num)

        planets = [p for p in PLANETS if re.search(rf"\b{re.escape(p.lower())}\b", lower)]
        signs = [s for s in SIGN_NAMES if re.search(rf"\b{re.escape(s.lower())}\b", lower)]
        nakshatras = [n for n in VALID_NAKSHATRAS if n.lower() in lower]
        yogas = [y for y in VALID_YOGAS if y.lower() in lower]
        doshas = [d for d in VALID_DOSHAS if d.lower() in lower]
        dashas = [d for d in VALID_DASHAS if d.lower() in lower]

        topics = [
            topic
            for topic, keywords in TOPIC_KEYWORDS.items()
            if any(re.search(rf"\b{re.escape(k)}\b", lower) for k in keywords)
        ]

        return DetectedFactors(
            houses=houses,
            planets=planets,
            signs=signs,
            nakshatras=nakshatras,
            yogas=yogas,
            doshas=doshas,
            dashas=dashas,
            topics=topics,
        )


class RuleExtractor:
    """Extract candidate rules from processed document chunks.

    The extraction is entirely rule-based (keyword and regex detection
    plus a deterministic confidence heuristic) — it never trains or
    calls a language model, per the Knowledge Corpus requirement to
    avoid retraining or altering the AI Conversation Engine.
    """

    def __init__(self, detector: AstrologicalFactorDetector | None = None) -> None:
        self.detector = detector or AstrologicalFactorDetector()

    def extract(self, chunk: DocumentChunk) -> CandidateRuleDraft | None:
        """Return a candidate rule draft for a chunk, or None if not rule-like."""
        text = chunk.metadata.translated_text or chunk.text
        if not text or len(text.strip()) < MIN_TEXT_LENGTH:
            return None

        factors = self.detector.detect(text)
        if factors.is_empty():
            return None

        confidence = self._confidence(text, factors)
        conditions = self._build_conditions(factors)
        topic = factors.topics[0] if factors.topics else "general"
        subtopic = factors.topics[1] if len(factors.topics) > 1 else None

        return CandidateRuleDraft(
            chunk_id=chunk.id,
            source_book_title=chunk.metadata.book_title or chunk.metadata.book_id,
            language=chunk.metadata.language or "en",
            chapter=chunk.metadata.chapter or None,
            verse=chunk.metadata.verse or None,
            page=chunk.metadata.page_number,
            original_text=chunk.metadata.original_text or chunk.text,
            translated_text=chunk.metadata.translated_text,
            topic=topic,
            subtopic=subtopic,
            astrological_factors=factors,
            candidate_conditions=conditions,
            candidate_interpretation=text.strip(),
            confidence=confidence,
        )

    def extract_many(self, chunks: list[DocumentChunk]) -> list[CandidateRuleDraft]:
        drafts = [self.extract(chunk) for chunk in chunks]
        return [d for d in drafts if d is not None]

    def _build_conditions(self, factors: DetectedFactors) -> list[str]:
        conditions: list[str] = []
        for planet in factors.planets:
            for house in factors.houses:
                conditions.append(f"{planet} in house {house}")
        if not conditions:
            for planet in factors.planets:
                conditions.append(f"{planet} referenced")
            for house in factors.houses:
                conditions.append(f"house {house} referenced")
        for sign in factors.signs:
            conditions.append(f"{sign} referenced")
        for nakshatra in factors.nakshatras:
            conditions.append(f"{nakshatra} nakshatra referenced")
        for yoga in factors.yogas:
            conditions.append(f"{yoga} present")
        for dosha in factors.doshas:
            conditions.append(f"{dosha} present")
        for dasha in factors.dashas:
            conditions.append(f"{dasha} dasha referenced")
        return conditions

    def _confidence(self, text: str, factors: DetectedFactors) -> float:
        """Deterministic heuristic confidence in [0, 1].

        This is intentionally simple and explainable: more recognized
        factor categories and clearer condition-like phrasing raise
        confidence; excessive length (likely an unrelated passage that
        merely mentions a term in passing) lowers it.
        """
        score = 0.25
        score += min(factors.factor_category_count(), 4) * 0.1

        lower = text.lower()
        if any(marker in lower for marker in _CONDITION_MARKERS):
            score += 0.15

        length = len(text)
        if length > MAX_TEXT_LENGTH_FOR_FULL_CONFIDENCE:
            score -= 0.1
        elif MIN_TEXT_LENGTH <= length <= 400:
            score += 0.05

        return max(0.0, min(1.0, round(score, 3)))
