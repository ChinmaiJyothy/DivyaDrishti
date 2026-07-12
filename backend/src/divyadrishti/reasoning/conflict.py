"""Conflict detection for evidence."""

from divyadrishti.reasoning.models import Evidence
from divyadrishti.reasoning.sentiment import Sentiment, classify_sentiment, sentiments_match


def detect_conflicts(evidence_list: list[Evidence]) -> list[tuple[str, str]]:
    """Return pairs of rule IDs that conflict with each other."""
    conflicts: list[tuple[str, str]] = []
    for i, ev_a in enumerate(evidence_list):
        for ev_b in evidence_list[i + 1:]:
            if not _same_topic(ev_a, ev_b):
                continue
            if not sentiments_match(ev_a.explanation, ev_b.explanation):
                conflicts.append((ev_a.rule_id, ev_b.rule_id))
    return conflicts


def _same_topic(ev_a: Evidence, ev_b: Evidence) -> bool:
    """Heuristic: evidence is comparable if it shares a factor or topic in conditions."""
    text_a = f"{ev_a.explanation} {' '.join(ev_a.matched_conditions)}".lower()
    text_b = f"{ev_b.explanation} {' '.join(ev_b.matched_conditions)}".lower()
    tokens_a = set(text_a.split())
    tokens_b = set(text_b.split())
    return bool(tokens_a & tokens_b)


def resolve_conflicts(
    evidence_list: list[Evidence],
    question: str,
) -> tuple[list[Evidence], list[Evidence]]:
    """Split evidence into supporting and conflicting relative to the question.

    Supporting evidence has the same sentiment as the question.
    Conflicting evidence has the opposite sentiment.
    """
    question_sentiment = classify_sentiment(question)
    supporting: list[Evidence] = []
    conflicting: list[Evidence] = []

    for ev in evidence_list:
        ev_sentiment = classify_sentiment(ev.explanation)
        if question_sentiment == Sentiment.NEGATIVE:
            if ev_sentiment == Sentiment.NEGATIVE:
                supporting.append(ev)
            elif ev_sentiment == Sentiment.POSITIVE:
                conflicting.append(ev)
            else:
                supporting.append(ev)
        else:
            if ev_sentiment == Sentiment.POSITIVE:
                supporting.append(ev)
            elif ev_sentiment == Sentiment.NEGATIVE:
                conflicting.append(ev)
            else:
                supporting.append(ev)

    return supporting, conflicting
