from divyadrishti.ai import AIConversationEngine, AIGateway, MockProvider


def test_conversation_engine_respond():
    engine = AIConversationEngine(gateway=AIGateway(provider=MockProvider()))
    reasoning = {
        "domain": "marriage",
        "matched_rules": [{"rule_id": "BPHS_7TH_001", "source": "BPHS"}],
        "supporting_evidence": [{"rule_id": "BPHS_7TH_001", "source": "BPHS"}],
        "conflicting_evidence": [],
        "overall_confidence": 72.5,
        "references": ["BPHS"],
        "suggested_follow_up_topics": ["Timing of marriage"],
    }

    response = engine.respond("Will I have a happy marriage?", reasoning)

    assert response.direct_answer
    assert response.interpretation
    assert response.references
    assert response.follow_up_questions


def test_conversation_engine_stream():
    engine = AIConversationEngine(gateway=AIGateway(provider=MockProvider()))
    chunks = list(engine.stream("Will I marry?", {"domain": "marriage"}))
    assert chunks
    assert "Jupiter" in "".join(chunks)
