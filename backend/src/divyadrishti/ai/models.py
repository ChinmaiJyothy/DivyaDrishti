"""Pydantic models for the AI Conversation and Interpretation Engine."""

from typing import Any

from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    """Structured response from the AI conversation engine."""

    direct_answer: str
    interpretation: str
    supporting_factors: list[str] = Field(default_factory=list)
    conflicting_factors: list[str] = Field(default_factory=list)
    overall_confidence: float = Field(default=0.0, ge=0.0, le=100.0)
    references: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    language: str = "en"


class PromptTemplate(BaseModel):
    """A loaded prompt template."""

    name: str
    version: str
    template: str
    variables: list[str] = Field(default_factory=list)


class TokenUsage(BaseModel):
    """Token accounting for a generation request."""

    provider: str
    prompt_chars: int
    completion_chars: int
    model: str | None = None


class GatewayRequest(BaseModel):
    """Request object passed to the AI Gateway."""

    system_prompt: str
    user_prompt: str
    max_tokens: int = 1024
    temperature: float = 0.7
    json_mode: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
