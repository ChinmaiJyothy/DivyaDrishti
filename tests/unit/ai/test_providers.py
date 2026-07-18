import pytest

from divyadrishti.ai import (
    AIGateway,
    AIResponse,
    GeminiProvider,
    GrokProvider,
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
)
from divyadrishti.ai.models import GatewayRequest


SAMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "direct_answer": {"type": "string"},
        "interpretation": {"type": "string"},
    },
    "required": ["direct_answer", "interpretation"],
}


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


def test_provider_generate_response_returns_ai_response():
    provider = MockProvider()
    response = provider.generate_response("system", "user", SAMPLE_SCHEMA)
    assert isinstance(response, AIResponse)
    assert response.direct_answer
    assert response.interpretation


@pytest.mark.parametrize(
    "provider_name, expected_class",
    [
        ("mock", MockProvider),
        ("openai", OpenAIProvider),
        ("grok", GrokProvider),
        ("gemini", GeminiProvider),
        ("ollama", OllamaProvider),
    ],
)
def test_gateway_selects_provider(provider_name, expected_class):
    gateway = AIGateway(provider_name=provider_name)
    assert isinstance(gateway.provider, expected_class)


def test_gateway_generate_response_returns_ai_response():
    gateway = AIGateway(provider=MockProvider())
    request = GatewayRequest(system_prompt="system", user_prompt="user")
    response = gateway.generate_response(request, SAMPLE_SCHEMA)
    assert isinstance(response, AIResponse)
    assert response.direct_answer
    assert response.interpretation


def test_gateway_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        AIGateway(provider_name="unknown")
