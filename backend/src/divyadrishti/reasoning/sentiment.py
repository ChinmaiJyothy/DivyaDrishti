"""Lightweight sentiment analysis for interpretation text.

This is intentionally deterministic and rule-based. It does NOT use an LLM.
"""

from enum import Enum


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


POSITIVE_WORDS = {
    "happy", "harmonious", "stable", "successful", "wealth", "prosperity",
    "benefic", "auspicious", "fortunate", "fortunate", "good", "strong",
    "support", "success", "recognition", "vitality", "healing", "wisdom",
    "spiritual", "growth", "leadership", "comfort", "joy", "gain", "profit",
}

NEGATIVE_WORDS = {
    "delay", "delayed", "obstacle", "conflict", "disease", "suffering",
    "affliction", "malefic", "unhappy", "unstable", "poverty", "loss",
    "debt", "trouble", "problem", "difficulty", "break", "separation",
    "miserable", "weak", "debilitated", "combust", "adverse", "negative",
    "misfortune", "struggle", "lesson", "karmic", "intensity",
}


def score_text(text: str) -> dict[Sentiment, int]:
    """Count positive and negative sentiment tokens in a text."""
    text = text.lower()
    tokens = set(text.split())

    positive = len(tokens & POSITIVE_WORDS)
    negative = len(tokens & NEGATIVE_WORDS)

    return {Sentiment.POSITIVE: positive, Sentiment.NEGATIVE: negative}


def classify_sentiment(text: str) -> Sentiment:
    """Classify text as positive, negative, or neutral."""
    scores = score_text(text)
    if scores[Sentiment.POSITIVE] > scores[Sentiment.NEGATIVE]:
        return Sentiment.POSITIVE
    if scores[Sentiment.NEGATIVE] > scores[Sentiment.POSITIVE]:
        return Sentiment.NEGATIVE
    return Sentiment.NEUTRAL


def sentiments_match(text_a: str, text_b: str) -> bool:
    """Return True if two texts have the same sentiment."""
    return classify_sentiment(text_a) == classify_sentiment(text_b)
