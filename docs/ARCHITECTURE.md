# DivyaDrishti Architecture

## Overview

This document describes the high-level architecture of DivyaDrishti.

## Core Principles

- Explainability first
- Separation of deterministic calculation and natural language generation
- Modular, scalable, maintainable

## System Components

- Frontend (Next.js)
- Backend (FastAPI)
- Database (SQLite / PostgreSQL)
- Document Knowledge Processing Pipeline
- Astrology Engine
- Evidence & Rule Evaluation Engine
- Reasoning Engine
- Knowledge Base
- Conversation Engine
- AI / LLM Provider

## Component Diagrams

## Reasoning Data Flow

```text
User Question
    ↓
Birth Chart (Astrology Engine)
    ↓
Knowledge Retrieval Engine
    ↓
Evidence & Rule Evaluation Engine
    ↓
Structured ReasoningTrace
    ↓
LLM Conversation Engine
    ↓
Natural Language Response
```

## Document Data Flow

```text
Uploaded Book (PDF, Markdown, TXT, OCR)
    ↓
Document Extractor
    ↓
Language Detector
    ↓
Semantic Chunker
    ↓
Embedding Generator
    ↓
Vector Store (ChromaDB)
    ↓
Document Retrieval Engine
    ↓
Reasoning Engine
    ↓
LLM Conversation Engine
```

## Component Details

### Document Knowledge Processing Pipeline

The Document Pipeline transforms books into a structured, searchable knowledge base.

Responsibilities:
- Extract text from PDF, Markdown, TXT, and scanned PDFs.
- Detect and preserve language.
- Generate semantic chunks.
- Generate embeddings.
- Store chunks in a vector store.
- Generate citations.

### Evidence & Rule Evaluation Engine

The Evidence Engine evaluates individual rules against the birth chart.

Responsibilities:
- Evaluate each rule against the birth chart.
- Score evidence and compute confidence.
- Generate `Evidence` objects.

### Astrological Reasoning Engine

The Astrological Reasoning Engine orchestrates the full analytical workflow.

Responsibilities:
- Understand the user's question and determine the astrology domain.
- Determine relevant astrological entities.
- Retrieve relevant rules from the Knowledge Engine.
- Evaluate every rule.
- Determine matched, partially matched, and unmatched rules.
- Score rules with weight, confidence, priority, source, and evidence.
- Resolve conflicts without ignoring any evidence.
- Generate structured `ReasoningResult` / `ReasoningTrace`.
- Never generate natural language.
- Never communicate with users.

Components:
- `QuestionAnalyzer`
- `RuleMatcher`
- `EvidenceEvaluator`
- `ConflictResolver`
- `ConfidenceCalculator`
- `ReasoningAggregator`
- `ReasoningSerializer`

The `ReasoningTrace` is the only input the LLM receives for astrological reasoning.

### AI Conversation & Interpretation Engine

The AI Conversation Engine converts structured reasoning into natural-language responses.

Responsibilities:
- Build prompts from reasoning, context, history, and preferences.
- Interface with a provider-agnostic LLM layer.
- Generate structured `AIResponse`.
- Support streaming and structured output.
- Maintain conversation memory.
- Support multilingual responses.
- Cite classical sources from the reasoning trace.
- Apply safety guardrails.

Components:
- `LLMProvider` interface and adapters (`OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`, `OllamaProvider`, `MockProvider`)
- `AIGateway` — provider selection, retry, timeout, fallback, logging
- `PromptManager` — external Jinja2 templates with versioning and validation
- `ContextBuilder` — assembles prompt context with truncation
- `ConversationMemory` — preferences and history
- `LanguageService` — localization and translation
- `SafetyGuard` — disallowed content and language sanitization

### Adaptive Knowledge Learning & Continuous Improvement

The Learning system enables DivyaDrishti to improve from feedback, admin corrections, and new books without retraining the LLM or modifying original classical texts.

Responsibilities:
- Collect user feedback.
- Manage rule versions and approval workflows.
- Analyze rule quality.
- Detect duplicate and conflicting rules.
- Monitor new book imports.
- Generate knowledge analytics.
- Maintain audit logs.
- Export knowledge, feedback, and metrics.

Components:
- `FeedbackManager`
- `RuleVersionManager`
- `QualityAnalyzer`
- `ConflictAnalyzer`
- `BookImportMonitor`
- `KnowledgeAnalytics`
- `AuditLogger`
- `KnowledgeExporter`

### Explainability Engine (XAI)

The Explainability Engine converts structured `ReasoningResult` into a transparent, traversable `ExplainabilityReport` with no LLM involvement.

Responsibilities:
- Build a reasoning graph.
- Trace every rule and its source.
- Explain supporting and conflicting evidence.
- Break down confidence into contributions.
- Collect classical references.
- Generate frontend visualization data.
- Identify limitations.

Components:
- `ExplainabilityEngine`
- `ReasoningGraphBuilder`
- `RuleTracer`
- `EvidenceExplainer`
- `ConfidenceExplainer`
- `ReferenceCollector`
- `VisualizationBuilder`
- `ReportSerializer`

### Authentication, User Profiles & Birth Chart Management

This module provides persistent identity, preference, profile, and conversation storage.

Responsibilities:
- Register and authenticate users.
- Issue and rotate JWT access/refresh tokens.
- Hash passwords with Argon2id.
- Manage user roles and permissions.
- Store user preferences and multiple birth profiles.
- Persist generated birth charts, planet positions, houses, and dashas.
- Store conversation history, messages, reasoning results, and explainability reports.
- Collect user feedback and uploaded books.
- Maintain audit logs and knowledge versions.
- Enforce resource ownership and soft deletes.

Components:
- `AuthenticationService`
- `UserService`
- `PreferenceService`
- `BirthProfileService`
- `BirthChartService`
- `ConversationService`
- `FeedbackService`
- `AuthorizationService`
- `UserRepository`
- `BirthProfileRepository`
- `ConversationRepository`
- `PreferenceRepository`
- `FeedbackRepository`
- Security: `hash_password`, `verify_password`, JWT tokens, `PermissionMiddleware`, `InMemoryRateLimiter`
- Database models: `User`, `Role`, `UserPreference`, `BirthProfile`, `BirthChart`, `PlanetPosition`, `HousePosition`, `Dasha`, `Conversation`, `Message`, `ReasoningResult`, `ExplainabilityReport`, `Feedback`, `UploadedBook`, `KnowledgeVersion`, `AuditLog`, `RefreshToken`, `UserSession`
- API routers: `auth`, `users`, `birth_profiles`, `conversations`, `preferences`, `feedback`

## Deployment Architecture

## Future Considerations
