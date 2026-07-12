"""LLM provider adapters for the AI Conversation Engine."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

import httpx


class LLMProvider(ABC):
    """Provider-agnostic interface for LLM adapters."""

    def __init__(self, model: str | None = None, **kwargs: Any) -> None:
        self.model = model or self.default_model()
        self.config = kwargs

    @abstractmethod
    def default_model(self) -> str:
        """Return the default model for this provider."""

    @abstractmethod
    def generate(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.7, json_mode: bool = False
    ) -> str:
        """Generate a completion string."""

    def stream(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.7
    ) -> Iterator[str]:
        """Generate a streaming completion."""
        yield self.generate(system_prompt, user_prompt, max_tokens, temperature)

    def generate_structured(
        self, system_prompt: str, user_prompt: str, schema: dict[str, Any], max_tokens: int = 1024, temperature: float = 0.7
    ) -> dict[str, Any]:
        """Generate a structured JSON response."""
        json_prompt = (
            f"{user_prompt}\n\nRespond with a single JSON object matching this schema:\n"
            f"{schema}"
        )
        text = self.generate(system_prompt, json_prompt, max_tokens, temperature, json_mode=True)
        import json

        return json.loads(text)

    def supports_streaming(self) -> bool:
        return False

    def supports_json(self) -> bool:
        return False

    def supports_function_calling(self) -> bool:
        return False


class MockProvider(LLMProvider):
    """Deterministic mock provider for testing."""

    def default_model(self) -> str:
        return "mock"

    def generate(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.7, json_mode: bool = False
    ) -> str:
        if json_mode:
            return self._mock_json()
        return self._mock_text()

    def _mock_text(self) -> str:
        return (
            "The chart shows a supportive Jupiter influence on the 7th house, which indicates "
            "a generally favorable foundation for marriage. However, Saturn's presence also suggests "
            "potential delays. Overall, the outlook is positive but patience is advised."
        )

    def _mock_json(self) -> str:
        import json

        return json.dumps(
            {
                "direct_answer": "Marriage is indicated but may be delayed.",
                "interpretation": "Jupiter supports the 7th house, while Saturn adds delays.",
                "supporting_factors": ["Jupiter in 7th house"],
                "conflicting_factors": ["Saturn in 7th house"],
                "overall_confidence": 72.5,
                "references": ["Brihat Parashara Hora Shastra"],
                "follow_up_questions": ["When can I expect to get married?"],
            },
            ensure_ascii=False,
        )

    def stream(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.7
    ) -> Iterator[str]:
        for token in self._mock_text().split():
            yield token + " "

    def supports_streaming(self) -> bool:
        return True


class OpenAIProvider(LLMProvider):
    """OpenAI adapter."""

    def __init__(self, model: str | None = None, api_key: str | None = None, base_url: str | None = None, **kwargs: Any) -> None:
        super().__init__(model=model, **kwargs)
        self.api_key = api_key
        self.base_url = base_url

    def default_model(self) -> str:
        return "gpt-4o-mini"

    def generate(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.7, json_mode: bool = False
    ) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("openai is required for OpenAIProvider.") from exc

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        extra: dict[str, Any] = {}
        if json_mode:
            extra["response_format"] = {"type": "json_object"}
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            **extra,
        )
        return response.choices[0].message.content or ""

    def stream(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.7
    ) -> Iterator[str]:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("openai is required for OpenAIProvider.") from exc

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    def supports_streaming(self) -> bool:
        return True

    def supports_json(self) -> bool:
        return True

    def supports_function_calling(self) -> bool:
        return True


class AnthropicProvider(LLMProvider):
    """Anthropic adapter using httpx."""

    def __init__(self, model: str | None = None, api_key: str | None = None, base_url: str = "https://api.anthropic.com/v1", **kwargs: Any) -> None:
        super().__init__(model=model, **kwargs)
        self.api_key = api_key
        self.base_url = base_url

    def default_model(self) -> str:
        return "claude-3-5-sonnet-20240620"

    def generate(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.7, json_mode: bool = False
    ) -> str:
        headers = {
            "x-api-key": self.api_key or "",
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        response = httpx.post(f"{self.base_url}/messages", headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]

    def supports_json(self) -> bool:
        return True


class GeminiProvider(LLMProvider):
    """Google Gemini adapter using httpx."""

    def __init__(self, model: str | None = None, api_key: str | None = None, **kwargs: Any) -> None:
        super().__init__(model=model, **kwargs)
        self.api_key = api_key

    def default_model(self) -> str:
        return "gemini-1.5-flash"

    def generate(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.7, json_mode: bool = False
    ) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            f"?key={self.api_key}"
        )
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}
            ],
            "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
        }
        response = httpx.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


class OllamaProvider(LLMProvider):
    """Ollama adapter for local models."""

    def __init__(self, model: str | None = None, base_url: str = "http://localhost:11434", **kwargs: Any) -> None:
        super().__init__(model=model, **kwargs)
        self.base_url = base_url

    def default_model(self) -> str:
        return "llama3.1"

    def generate(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.7, json_mode: bool = False
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        response = httpx.post(f"{self.base_url}/api/chat", json=payload, timeout=120.0)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]

    def stream(
        self, system_prompt: str, user_prompt: str, max_tokens: int = 1024, temperature: float = 0.7
    ) -> Iterator[str]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        with httpx.stream("POST", f"{self.base_url}/api/chat", json=payload, timeout=120.0) as response:
            for line in response.iter_lines():
                if not line:
                    continue
                import json

                data = json.loads(line)
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content

    def supports_streaming(self) -> bool:
        return True
