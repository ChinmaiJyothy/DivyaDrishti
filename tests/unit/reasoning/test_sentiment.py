from divyadrishti.reasoning.sentiment import classify_sentiment, sentiments_match, Sentiment


def test_positive_sentiment():
    assert classify_sentiment("A happy and harmonious marriage") == Sentiment.POSITIVE


def test_negative_sentiment():
    assert classify_sentiment("Delayed and conflicted marriage") == Sentiment.NEGATIVE


def test_neutral_sentiment():
    assert classify_sentiment("The 7th house is the house of marriage") == Sentiment.NEUTRAL


def test_sentiments_match():
    assert sentiments_match("Happy marriage", "Harmonious union") is True
    assert sentiments_match("Happy marriage", "Conflict and delay") is False
