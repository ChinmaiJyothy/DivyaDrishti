import pytest

from divyadrishti.learning import FeedbackEntry, FeedbackManager


def test_feedback_add():
    manager = FeedbackManager()
    entry = FeedbackEntry(
        conversation_id="conv-1",
        question="Will I marry?",
        reasoning_trace={},
        response="Yes, likely.",
        rating="Helpful",
    )
    manager.add(entry)
    assert len(manager.feedback) == 1


def test_feedback_invalid_rating():
    manager = FeedbackManager()
    entry = FeedbackEntry(
        conversation_id="conv-1",
        question="Will I marry?",
        reasoning_trace={},
        response="Yes.",
        rating="Amazing",
    )
    with pytest.raises(ValueError):
        manager.add(entry)


def test_feedback_summary():
    manager = FeedbackManager()
    for rating in ["Helpful", "Helpful", "Not Helpful"]:
        manager.add(
            FeedbackEntry(
                conversation_id="conv-1",
                question="?",
                reasoning_trace={},
                response=".",
                rating=rating,
            )
        )
    summary = manager.summary()
    assert summary["Helpful"] == 2
    assert summary["Not Helpful"] == 1
