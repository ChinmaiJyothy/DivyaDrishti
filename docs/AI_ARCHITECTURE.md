# AI Architecture

## Persona

The AI behaves as an experienced, compassionate, and professional Vedic astrologer.

- Calm and respectful
- Patient and thoughtful
- Honest about uncertainty
- Balanced, never dramatic or fear-based
- Uses tentative language: "indicates", "suggests", "favorable for"
- Presents astrology as interpretation, not certainty

## System Prompt

The system prompt is loaded from `prompts/system.md` and augmented with safety and tone instructions. It instructs the model to base every statement on the provided `ReasoningTrace` and to avoid inventing astrological facts.

## Provider Architecture

The AI layer is provider-agnostic. All providers implement `LLMProvider`:

```python
class LLMProvider:
    def generate(self, system_prompt, user_prompt, max_tokens, temperature, json_mode) -> str
    def stream(self, system_prompt, user_prompt, max_tokens, temperature) -> Iterator[str]
    def generate_structured(self, system_prompt, user_prompt, schema, max_tokens, temperature) -> dict
    def generate_response(self, system_prompt, user_prompt, schema, max_tokens, temperature) -> AIResponse
    def supports_streaming(self) -> bool
    def supports_json(self) -> bool
    def supports_function_calling(self) -> bool
```

Supported adapters:

- `MockProvider` — deterministic testing provider
- `OpenAIProvider` — OpenAI GPT models
- `GrokProvider` — xAI Grok (OpenAI-compatible API)
- `AnthropicProvider` — Anthropic Claude (httpx)
- `GeminiProvider` — Google Gemini (httpx)
- `OllamaProvider` — Local Ollama models

Provider selection is configurable via the `LLM_PROVIDER` environment variable:

```bash
LLM_PROVIDER=grok|gemini|openai|ollama|mock
```

Set the corresponding API key for the chosen provider (e.g. `OPENAI_API_KEY`, `GROK_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`).
No application code changes are required when switching providers.

The `generate_response` method returns a validated `AIResponse` object, so the Conversation Engine is always provider-agnostic.

## AI Gateway

`AIGateway` is the single interface between the application and the LLM. Responsibilities:

- Provider selection
- Retry handling
- Timeout handling
- Streaming support
- Token accounting
- Logging
- Fallback provider support

The application never talks directly to a provider.

## Prompt Manager

`PromptManager` loads external Jinja2 templates from `prompts/`:

- `system.md`
- `career.md`
- `marriage.md`
- `finance.md`
- `health.md`
- `education.md`
- `relationship.md`
- `personality.md`
- `report_generation.md`

Each prompt supports Jinja variables, versioning via `prompts/manifest.json`, and validation.

## Context Builder

`ContextBuilder` assembles the final user prompt from:

- User question
- Chart summary
- Reasoning result
- Matched rules
- Supporting and conflicting evidence
- Confidence score
- Conversation history
- User preferences
- Source references

It truncates intelligently to stay within model limits.

## Conversation Memory

`ConversationMemory` stores:

- Preferred language
- Explanation depth
- Conversation history
- Frequently discussed topics

History is truncated to a configurable maximum number of exchanges.

## Response Structure

The AI returns a structured `AIResponse`:

```json
{
  "direct_answer": "...",
  "interpretation": "...",
  "supporting_factors": [...],
  "conflicting_factors": [...],
  "overall_confidence": 72.5,
  "references": [...],
  "follow_up_questions": [...],
  "language": "en"
}
```

The final user-facing response is generated from these fields and is conversational, not JSON.

## Multilingual Support

`LanguageService` supports English, Hindi, Kannada, Telugu, Tamil, Malayalam, Gujarati, and Marathi. The LLM is instructed to respond in the preferred language when possible. If the provider cannot generate the language, a `deep-translator` based adapter is available.

## Source Citations

Responses include only references present in the `ReasoningTrace`. The AI never fabricates citations.

## Safety

`SafetyGuard` filters disallowed content:

- Medical advice
- Legal advice
- Financial guarantees
- Fear-based predictions

It also sanitizes deterministic language into tentative phrasing.

## Extensibility

- Add new providers by implementing `LLMProvider`.
- Add new prompt templates to `prompts/`.
- Swap `ConversationMemory` for a persistent store.
- Extend `ContextBuilder` with timing and transit data.
