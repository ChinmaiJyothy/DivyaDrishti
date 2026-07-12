from divyadrishti.ai import ContextBuilder


def test_context_builder_includes_question_and_reasoning():
    builder = ContextBuilder()
    reasoning = {
        "domain": "marriage",
        "matched_rules": ["Jupiter in 7th"],
        "supporting_evidence": ["Jupiter supports marriage"],
        "conflicting_evidence": ["Saturn delays"],
        "overall_confidence": 75.0,
        "references": ["BPHS"],
    }
    context = builder.build("When will I marry?", reasoning)
    assert "When will I marry?" in context
    assert "BPHS" in context
    assert "75.0" in context


def test_context_builder_truncates():
    builder = ContextBuilder(max_chars=50)
    reasoning = {"matched_rules": ["x" * 1000]}
    context = builder.build("question", reasoning)
    assert len(context) <= 200
