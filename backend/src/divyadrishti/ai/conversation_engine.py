"""AI Conversation and Interpretation Engine for DivyaDrishti."""

import logging
from pathlib import Path
from typing import Any

from divyadrishti.ai.context_builder import ContextBuilder
from divyadrishti.ai.gateway import AIGateway
from divyadrishti.ai.language import LanguageService
from divyadrishti.ai.memory import ConversationMemory
from divyadrishti.ai.models import AIResponse, GatewayRequest
from divyadrishti.ai.prompt_manager import PromptManager
from divyadrishti.ai.safety import SafetyGuard

logger = logging.getLogger(__name__)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "direct_answer": {"type": "string"},
        "interpretation": {"type": "string"},
        "supporting_factors": {"type": "array", "items": {"type": "string"}},
        "conflicting_factors": {"type": "array", "items": {"type": "string"}},
        "overall_confidence": {"type": "number"},
        "references": {"type": "array", "items": {"type": "string"}},
        "follow_up_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "direct_answer",
        "interpretation",
        "supporting_factors",
        "conflicting_factors",
        "overall_confidence",
        "references",
        "follow_up_questions",
    ],
}


class AIConversationEngine:
    """Generate natural-language astrological responses from structured reasoning."""

    def __init__(
        self,
        gateway: AIGateway | None = None,
        prompt_manager: PromptManager | None = None,
        context_builder: ContextBuilder | None = None,
        memory: ConversationMemory | None = None,
        language_service: LanguageService | None = None,
        safety_guard: SafetyGuard | None = None,
    ) -> None:
        self.gateway = gateway or AIGateway()
        self.prompt_manager = prompt_manager or PromptManager(Path(__file__).parent.parent.parent.parent.parent / "prompts")
        self.context_builder = context_builder or ContextBuilder()
        self.memory = memory or ConversationMemory()
        self.language_service = language_service or LanguageService()
        self.safety_guard = safety_guard or SafetyGuard()

    def respond(
        self,
        question: str,
        reasoning: dict[str, Any],
        chart_summary: str = "",
        language: str | None = None,
    ) -> AIResponse:
        """Generate a professional, natural-language response."""
        language = language or self.memory.get_preference("language", "en")
        self.memory.set_preference("language", language)

        system_prompt = self._build_system_prompt()
        user_prompt = self.context_builder.build(
            question=question,
            reasoning=reasoning,
            memory=self.memory,
            chart_summary=chart_summary,
            language=language,
        )

        request = GatewayRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=True,
        )

        response = self.gateway.generate_response(request, RESPONSE_SCHEMA)
        response.language = language
        response = self._enrich_response(response, reasoning)

        if language != "en":
            response = self._localize_response(response, language)

        self.memory.add_exchange(question, response.direct_answer)
        return response

    def stream(
        self,
        question: str,
        reasoning: dict[str, Any],
        chart_summary: str = "",
        language: str = "en",
    ):
        """Stream a response as a sequence of chunks."""
        system_prompt = self._build_system_prompt()
        user_prompt = self.context_builder.build(
            question=question,
            reasoning=reasoning,
            memory=self.memory,
            chart_summary=chart_summary,
            language=language,
        )
        request = GatewayRequest(system_prompt=system_prompt, user_prompt=user_prompt)
        yield from self.gateway.stream(request)

    def _build_system_prompt(self) -> str:
        """Build the system prompt from template and safety instructions."""
        system = self.prompt_manager.render("system", {})
        safety = (
            "\n\nSafety and tone guidelines:\n"
            "- Never invent astrological facts.\n"
            "- Never contradict the provided reasoning.\n"
            "- Avoid medical, legal, or financial advice.\n"
            "- Avoid fear-based or deterministic language.\n"
            "- Present astrology as interpretation, not certainty.\n"
            "- Cite classical sources only if they appear in the reasoning."
        )
        return system + safety

    def _enrich_response(self, response: AIResponse, reasoning: dict[str, Any]) -> AIResponse:
        """Add references and follow-up topics from the reasoning trace."""
        if not response.references and reasoning.get("references"):
            response.references = reasoning["references"]
        if not response.follow_up_questions and reasoning.get("suggested_follow_up_topics"):
            response.follow_up_questions = reasoning["suggested_follow_up_topics"]
        response.direct_answer = self.safety_guard.sanitize(response.direct_answer)
        response.interpretation = self.safety_guard.sanitize(response.interpretation)
        return response

    def _localize_response(self, response: AIResponse, language: str) -> AIResponse:
        """Translate the response fields to the requested language."""
        response.direct_answer = self.language_service.localize(response.direct_answer, language)
        response.interpretation = self.language_service.localize(response.interpretation, language)
        response.supporting_factors = [
            self.language_service.localize(f, language) for f in response.supporting_factors
        ]
        response.conflicting_factors = [
            self.language_service.localize(f, language) for f in response.conflicting_factors
        ]
        return response
