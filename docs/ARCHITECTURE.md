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

The Evidence Engine sits between the Knowledge Base and the LLM.

Responsibilities:
- Collect relevant rules from the Knowledge Retrieval Engine.
- Evaluate each rule against the birth chart.
- Score evidence and compute confidence.
- Detect conflicting rules.
- Group evidence by topic.
- Aggregate into a `ReasoningTrace`.

The `ReasoningTrace` is the only input the LLM receives for astrological reasoning.

## Deployment Architecture

## Future Considerations
