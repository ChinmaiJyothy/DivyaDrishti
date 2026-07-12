from divyadrishti.ai import AIGateway, MockProvider


def test_mock_provider_generate():
    provider = MockProvider()
    text = provider.generate("system", "user")
    assert "Jupiter" in text


def test_mock_provider_stream():
    provider = MockProvider()
    chunks = list(provider.stream("system", "user"))
    assert chunks
    assert "Jupiter" in "".join(chunks)


def test_mock_provider_generate_structured():
    provider = MockProvider()
    data = provider.generate_structured("system", "user", {})
    assert "direct_answer" in data


def test_gateway_selects_provider():
    gateway = AIGateway(provider_name="mock")
    assert gateway.provider.__class__.__name__ == "MockProvider"
