"""Tests for automatic rule extraction from semantic chunks."""

from divyadrishti.documents.models import ChunkMetadata, DocumentChunk
from divyadrishti.knowledge.rule_extraction import RuleExtractor


def test_rule_extractor_extracts_astrological_factors():
    chunk = DocumentChunk(
        text="Jupiter in the 7th house gives a happy marriage.",
        metadata=ChunkMetadata(
            book_id="BPHS",
            book_title="Brihat Parashara Hora Shastra",
            language="en",
            chapter="1",
            verse="5",
            page_number=12,
        ),
    )

    extractor = RuleExtractor()
    draft = extractor.extract(chunk)

    assert draft is not None
    assert draft.candidate_rule_id.startswith("CAND_")
    assert draft.source_book_title == "Brihat Parashara Hora Shastra"
    assert draft.topic == "marriage"
    assert "Jupiter" in draft.astrological_factors.planets
    assert 7 in draft.astrological_factors.houses
    assert draft.candidate_conditions
    assert "Jupiter in house 7" in draft.candidate_conditions
    assert "happy marriage" in draft.candidate_interpretation
    assert 0.0 < draft.confidence <= 1.0
    assert draft.page == 12


def test_rule_extractor_skips_non_rule_text():
    chunk = DocumentChunk(
        text="This is a short sentence.",
        metadata=ChunkMetadata(
            book_id="BPHS",
            book_title="Test Book",
            language="en",
        ),
    )

    extractor = RuleExtractor()
    assert extractor.extract(chunk) is None
