"""AI Gateway for the AI Conversation Engine."""

import logging
import os
from collections.abc import Callable, Iterator
from typing import Any

from divyadrishti.ai.models import GatewayRequest, TokenUsage
from divyadrishti.ai.providers import (
    AnthropicProvider,
    GeminiProvider,
    LLMProvider,
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3

PROVIDER_MAP: dict[str, type[LLMProvider]] = {
    "mock": MockProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
}


class AIGateway:
    """Provider-agnostic gateway for prompt construction, provider selection, retries, and logging."""

    def __init__(
        self,
        provider: LLMProvider | None = None,
        provider_name: str | None = None,
        fallback_name: str | None = None,
        max_retries: int = MAX_RETRIES,
        timeout: float = 60.0,
    ) -> None:
        provider_name = provider_name or os.getenv("LLM_PROVIDER")
        if provider is None and provider_name is None:
            raise ValueError(
                "LLM provider not configured. Set LLM_PROVIDER environment variable or pass provider explicitly."
            )
        self.provider = provider or self._build_provider(provider_name)
        self.fallback_name = fallback_name or os.getenv("LLM_FALLBACK_PROVIDER")
        self.max_retries = max_retries
        self.timeout = timeout
        self.usage_log: list[TokenUsage] = []

    def _build_provider(self, name: str) -> LLMProvider:
        if name not in PROVIDER_MAP:
            raise ValueError(f"Unknown provider: {name}")

        cls = PROVIDER_MAP[name]
        config = self._provider_config(name)
        return cls(**config)

    def _provider_config(self, name: str) -> dict[str, Any]:
        model = os.getenv("LLM_MODEL")
        if name == "openai":
            return {"model": model, "api_key": os.getenv("OPENAI_API_KEY")}
        if name == "anthropic":
            return {"model": model, "api_key": os.getenv("ANTHROPIC_API_KEY")}
        if name == "gemini":
            return {"model": model, "api_key": os.getenv("GEMINI_API_KEY")}
        if name == "ollama":
            return {"model": model, "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")}
        return {"model": model}

    def generate(self, request: GatewayRequest) -> str:
        """Generate a completion with retry and fallback."""

        def call(provider: LLMProvider) -> str:
            return provider.generate(
                request.system_prompt,
                request.user_prompt,
                request.max_tokens,
                request.temperature,
                request.json_mode,
            )

        return self._call_with_retry(call)

    def stream(self, request: GatewayRequest) -> Iterator[str]:
        """Generate a streaming completion."""
        if not self.provider.supports_streaming():
            yield self.generate(request)
            return

        def call(provider: LLMProvider) -> Iterator[str]:
            return provider.stream(
                request.system_prompt,
                request.user_prompt,
                request.max_tokens,
                request.temperature,
            )

        result = self._call_with_retry(call)
        yield from result

    def generate_structured(self, request: GatewayRequest, schema: dict[str, Any]) -> dict[str, Any]:
        """Generate a structured JSON response."""

        def call(provider: LLMProvider) -> dict[str, Any]:
            return provider.generate_structured(
                request.system_prompt,
                request.user_prompt,
                schema,
                request.max_tokens,
                request.temperature,
            )

        return self._call_with_retry(call)

    def _call_with_retry(self, call: Callable[[LLMProvider], Any]) -> Any:
        last_error: Exception | None = None
        providers = [self.provider]
        if self.fallback_name and self.fallback_name in PROVIDER_MAP:
            providers.append(self._build_provider(self.fallback_name))

        for provider in providers:
            for attempt in range(self.max_retries):
                try:
                    result = call(provider)
                    self._log_usage(provider, result)
                    return result
                except Exception as exc:
                    last_error = exc
                    logger.warning("Provider %s attempt %s failed: %s", provider.__class__.__name__, attempt + 1, exc)

        raise last_error or RuntimeError("All providers failed.")

    def _log_usage(self, provider: LLMProvider, result: Any) -> None:
        completion = result if isinstance(result, str) else str(result)
        usage = TokenUsage(
            provider=provider.__class__.__name__,
            prompt_chars=0,
            completion_chars=len(completion),
            model=provider.model,
        )
        self.usage_log.append(usage)

    def supports_streaming(self) -> bool:
        return self.provider.supports_streaming()

    def supports_json(self) -> bool:
        return self.provider.supports_json()

    def supports_function_calling(self) -> bool:
        return self.provider.supports_function_calling()
