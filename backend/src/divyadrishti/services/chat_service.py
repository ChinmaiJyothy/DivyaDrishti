"""Chat service orchestrating the AI conversation, reasoning, and explainability pipeline."""

from typing import Any, Iterator

from sqlalchemy.orm import Session

from divyadrishti.ai.conversation_engine import AIConversationEngine
from divyadrishti.ai.memory import ConversationMemory
from divyadrishti.ai.models import AIResponse
from divyadrishti.explainability.engine import ExplainabilityEngine
from divyadrishti.knowledge.repository import KnowledgeRepository
from divyadrishti.knowledge.retrieval import KnowledgeRetrievalEngine
from divyadrishti.models import ExplainabilityReport, Message, ReasoningResult
from divyadrishti.reasoning.astrological.engine import AstrologicalReasoningEngine
from divyadrishti.reasoning.astrological.models import AstrologicalChart, ReasoningRequest
from divyadrishti.schemas.chat import ChatRequest
from divyadrishti.services.birth_chart_service import BirthChartService
from divyadrishti.services.birth_profile_service import BirthProfileService
from divyadrishti.services.conversation_service import ConversationService


class ChatService:
    """End-to-end chat service for Vedic astrology conversations."""

    def __init__(self, db: Session, knowledge_repository: KnowledgeRepository) -> None:
        self.db = db
        self.knowledge_repository = knowledge_repository
        self.conversation_service = ConversationService(db)
        self.birth_profile_service = BirthProfileService(db)
        self.birth_chart_service = BirthChartService(db)
        self.knowledge_engine = KnowledgeRetrievalEngine(knowledge_repository)
        self.reasoning_engine = AstrologicalReasoningEngine(self.knowledge_engine)
        self.explainability_engine = ExplainabilityEngine(knowledge_repository)
        self.ai_engine = AIConversationEngine(memory=ConversationMemory())

    def stream(self, conversation: Any, request: ChatRequest) -> Iterator[dict]:
        """Stream an assistant response for a conversation message.

        Yields SSE-shaped dictionaries: user, delta, metadata, error, done.
        """
        try:
            user_message = self.conversation_service.add_message(
                conversation.id,
                conversation.user_id,
                "user",
                request.content,
            )
            yield {
                "event": "user",
                "message_id": user_message.id,
                "role": "user",
                "content": user_message.content,
            }

            self._prime_memory(conversation)

            chart = self._build_chart(conversation)
            reasoning_result = self.reasoning_engine.reason(
                ReasoningRequest(question=request.content, chart=chart)
            )
            explainability_report = self.explainability_engine.explain(
                request.content, chart, reasoning_result
            )

            reasoning_for_engine = self._reasoning_for_engine(reasoning_result)
            chart_summary = self._chart_summary(conversation, chart)

            full_answer = ""
            for token in self.ai_engine.stream(
                question=request.content,
                reasoning=reasoning_for_engine,
                chart_summary=chart_summary,
                language=request.language,
            ):
                full_answer += token
                yield {"event": "delta", "content": token}

            ai_response = self._build_ai_response(
                full_answer=full_answer,
                reasoning_result=reasoning_result,
                explainability_report=explainability_report,
                language=request.language,
            )

            assistant_message = self.conversation_service.add_message(
                conversation.id,
                conversation.user_id,
                "assistant",
                full_answer,
                ai_response=ai_response.model_dump(),
            )

            self._attach_reasoning_and_explainability(
                assistant_message,
                conversation.id,
                reasoning_result,
                explainability_report,
            )

            yield {
                "event": "metadata",
                "message_id": assistant_message.id,
                "ai_response": ai_response.model_dump(),
                "reasoning_result": reasoning_result.model_dump(),
                "explainability_report": explainability_report.model_dump(),
                "follow_up_questions": ai_response.follow_up_questions,
                "confidence": ai_response.overall_confidence,
            }
            yield {"event": "done"}

        except Exception as exc:
            yield {"event": "error", "detail": str(exc)}

    def _prime_memory(self, conversation: Any) -> None:
        """Fill the conversation memory with previous user/assistant exchanges."""
        for msg in conversation.messages:
            if msg.role == "assistant" and msg.ai_response_json:
                answer = msg.ai_response_json.get("direct_answer", msg.content)
            else:
                continue
            # Find the preceding user message.
            user_content = ""
            for prev in conversation.messages:
                if prev.id < msg.id and prev.role == "user":
                    user_content = prev.content
            if user_content:
                self.ai_engine.memory.add_exchange(user_content, answer)

    def _build_chart(self, conversation: Any) -> AstrologicalChart:
        """Build an AstrologicalChart from the conversation's birth profile."""
        if not conversation.birth_profile_id:
            return AstrologicalChart()

        profile = self.birth_profile_service.get(
            conversation.birth_profile_id, conversation.user_id
        )
        if not profile:
            return AstrologicalChart()

        chart = self.birth_chart_service.get_latest_chart(profile.id)
        if not chart or not chart.chart_data:
            return AstrologicalChart()

        return self._to_astrological_chart(chart.chart_data)

    def _to_astrological_chart(self, chart_data: dict) -> AstrologicalChart:
        """Convert a raw chart JSON payload into an AstrologicalChart."""
        payload = {
            k: v
            for k, v in chart_data.items()
            if k in AstrologicalChart.model_fields
        }

        planets = chart_data.get("planets")
        if isinstance(planets, list):
            payload["planets"] = {
                p.get("name", p.get("planet", str(i))): p
                for i, p in enumerate(planets)
            }
        elif not isinstance(planets, dict):
            payload["planets"] = {}

        try:
            return AstrologicalChart(**payload)
        except Exception:
            return AstrologicalChart()

    def _chart_summary(self, conversation: Any, chart: AstrologicalChart) -> str:
        """Return a short text summary of the chart for the prompt."""
        profile = None
        if conversation.birth_profile_id:
            profile = self.birth_profile_service.get(
                conversation.birth_profile_id, conversation.user_id
            )
        parts = []
        if profile:
            parts.append(profile.profile_name)
        if chart.lagna:
            parts.append(f"{chart.lagna} lagna")
        if chart.moon_sign:
            parts.append(f"{chart.moon_sign} moon sign")
        if chart.maha_dasha:
            parts.append(f"{chart.maha_dasha} maha dasha")
        return ", ".join(parts) if parts else ""

    def _reasoning_for_engine(self, reasoning_result: Any) -> dict[str, Any]:
        """Build a plain dict for the AI conversation engine context."""
        references = [
            ev.source
            for ev in reasoning_result.supporting_evidence + reasoning_result.conflicting_evidence
            if ev.source
        ]
        return {
            "matched_rules": [r.model_dump() for r in reasoning_result.matched_rules],
            "supporting_evidence": [r.model_dump() for r in reasoning_result.supporting_evidence],
            "conflicting_evidence": [r.model_dump() for r in reasoning_result.conflicting_evidence],
            "overall_confidence": reasoning_result.overall_confidence,
            "reasoning_summary": reasoning_result.reasoning_summary,
            "references": list(dict.fromkeys(references)),
            "suggested_follow_up_topics": reasoning_result.suggested_follow_up_topics,
        }

    def _build_ai_response(
        self,
        full_answer: str,
        reasoning_result: Any,
        explainability_report: Any,
        language: str,
    ) -> AIResponse:
        """Build an AIResponse value object from reasoning and explainability."""
        supporting = [
            ev.explanation or ev.rule_id
            for ev in reasoning_result.supporting_evidence
            if ev.explanation or ev.rule_id
        ]
        conflicting = [
            ev.explanation or ev.rule_id
            for ev in reasoning_result.conflicting_evidence
            if ev.explanation or ev.rule_id
        ]
        references = [
            f"{ref.book} {ref.chapter or ''} {ref.verse or ''}".strip()
            for ref in explainability_report.classical_references
        ]
        return AIResponse(
            direct_answer=full_answer,
            interpretation=full_answer,
            supporting_factors=supporting,
            conflicting_factors=conflicting,
            overall_confidence=reasoning_result.overall_confidence,
            references=references,
            follow_up_questions=reasoning_result.suggested_follow_up_topics,
            language=language,
        )

    def _attach_reasoning_and_explainability(
        self,
        assistant_message: Message,
        conversation_id: int,
        reasoning_result: Any,
        explainability_report: Any,
    ) -> None:
        """Persist reasoning and explainability records for an assistant message."""
        reasoning_db = ReasoningResult(
            conversation_id=conversation_id,
            message_id=assistant_message.id,
            domain=reasoning_result.domain,
            chart_data=reasoning_result.relevant_factors.model_dump(),
            matched_rules_json=[r.model_dump() for r in reasoning_result.matched_rules],
            supporting_evidence_json=[r.model_dump() for r in reasoning_result.supporting_evidence],
            conflicting_evidence_json=[r.model_dump() for r in reasoning_result.conflicting_evidence],
            overall_confidence=reasoning_result.overall_confidence,
            reasoning_summary=reasoning_result.reasoning_summary,
        )
        explainability_db = ExplainabilityReport(
            conversation_id=conversation_id,
            message_id=assistant_message.id,
            report_data_json=explainability_report.model_dump(),
        )
        assistant_message.reasoning_results.append(reasoning_db)
        assistant_message.explainability_reports.append(explainability_db)
        self.db.add(reasoning_db)
        self.db.add(explainability_db)
        self.db.commit()


def get_chat_service(db: Session, knowledge_repository: KnowledgeRepository) -> ChatService:
    """Factory for ChatService."""
    return ChatService(db, knowledge_repository)
