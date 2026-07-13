# Chat Architecture

## Overview

The AI Chat module is a dedicated workspace for Vedic astrology conversations. It is designed to feel like a premium conversational AI (ChatGPT/Perplexity) while surfacing the structured reasoning, explainability, and birth-chart context that makes DivyaDrishti unique.

## Guiding Principles

- **Conversation-first**: The chat is the primary workspace; everything else is context.
- **Streaming first**: Assistant responses stream token-by-token with graceful cancellation and retry.
- **Trustworthy**: Every answer is paired with explainability data (why, evidence, references, confidence).
- **Context-aware**: Birth profile, planetary positions, dasha, and conversation history are always available to the AI.
- **Responsive**: Three-panel desktop layout collapses into drawers on mobile.

## Backend Architecture

### Flow

1. User sends a message to a conversation.
2. `ChatService` creates the user `Message` in the database.
3. `ChatService` loads the conversation's `birth_profile` and its latest `BirthChart`.
4. `ChatService` builds an `AstrologicalChart` from the chart JSON.
5. `AstrologicalReasoningEngine.reason(...)` uses the chart and question to find relevant knowledge rules and produce a `ReasoningResult`.
6. `ExplainabilityEngine.explain(...)` turns the `ReasoningResult` into an `ExplainabilityReport`.
7. `AIConversationEngine.stream(...)` streams the natural-language answer, grounded in the reasoning.
8. `ChatService` accumulates the streamed text and creates the assistant `Message`, storing:
   - `ai_response_json` as `AIResponse`
   - `reasoning_results` as `ReasoningResult`
   - `explainability_reports` as `ExplainabilityReport`
9. The endpoint returns the response as a `text/event-stream` with SSE events: `user`, `delta`, `metadata`, `error`, `done`.

### Key Components

- `services/chat_service.py` — orchestrates the chat pipeline.
- `api/v1/routers/chat.py` — `POST /chat/{conversation_id}` SSE endpoint.
- `schemas/chat.py` — `ChatRequest`, `ChatMessageEvent`, `ChatMetadataEvent`.
- `ai/conversation_engine.py` — `respond()` and `stream()` for structured and streaming responses.
- `reasoning/astrological/engine.py` — `AstrologicalReasoningEngine`.
- `explainability/engine.py` — `ExplainabilityEngine`.
- `knowledge/repository.py` / `knowledge/retrieval.py` — `KnowledgeRepository` and `KnowledgeRetrievalEngine`.

### Streaming

- `ChatService.stream()` returns `Iterator[dict]`.
- `chat.py` wraps it in `StreamingResponse(media_type="text/event-stream")`.
- SSE events are JSON encoded.
- `AbortController` / `signal` on the frontend cancels the stream and the LLM gateway stops yielding.

## Frontend Architecture

### Layout

```
app/(dashboard)/chat/
├── layout.tsx          # Chat layout with null context panel; ChatWorkspace owns sidebars
├── page.tsx            # ChatPage

components/chat/
├── chat-workspace.tsx     # Three-pane layout + mobile drawers
├── conversation-sidebar.tsx
├── conversation-list.tsx
├── chat-panel.tsx
├── chat-header.tsx
├── message-list.tsx
├── message-item.tsx
├── message-bubble.tsx
├── message-actions.tsx
├── chat-input.tsx
├── follow-up-suggestions.tsx
├── chat-context-panel.tsx
├── explainability-panel.tsx
├── reasoning-graph.tsx
├── confidence-breakdown.tsx
├── suggested-questions.tsx
└── welcome-chat.tsx
```

### State

- `useChat` hook in `frontend/hooks/use-chat.ts` owns:
  - `conversationId`
  - `messages` (local optimistic list)
  - `streaming` / `isLoading` / `error`
  - `stop`, `retry`, `regenerate`, `edit`, `delete` operations
- `useConversations` from `use-conversations.ts` provides list/search/archive/delete.
- `useCurrentProfileChart` and `useBirthProfiles` provide the birth chart context.
- `TanStack Query` caches `conversation` and `messages` and invalidates after mutations.

### Streaming Client

- `frontend/services/chat.service.ts` exposes `streamChatMessage`.
- Uses `fetch` with `ReadableStream` and an `AbortController`.
- Parses SSE `data:` lines and emits `onEvent` callbacks.
- `useChat` accumulates `delta` events into a streaming assistant message and commits it when `metadata` arrives.

### Explainability

- `Message` type includes `ai_response_json: AIResponse` and `explainability_report: ExplainabilityReport`.
- `MessageItem` renders a default `direct_answer` and an expandable `ExplainabilityPanel`.
- `ExplainabilityPanel` shows: Why, Evidence (supporting/conflicting), Classical References, Confidence Breakdown, Reasoning Graph, Limitations.

### Performance

- `MessageList` uses `react-window` or `react-virtuoso` for virtualized rendering.
- `Markdown` is rendered with `react-markdown` + `remark-gfm`.
- Code blocks are wrapped in a `pre`/`code` block with a copy button.
- Streaming only appends text; message objects are updated by mutation (not replaced) to avoid re-render thrash.

## Conversation Lifecycle

1. Create: `POST /conversations` (optionally with `birth_profile_id` and `domain`).
2. Send: `POST /chat/{conversation_id}` streams the assistant response.
3. Persist: user and assistant messages are stored with `ai_response_json`, `reasoning_results`, and `explainability_reports`.
4. Update: `PATCH /conversations/{conversation_id}` renames, archives, pins, or changes `birth_profile_id`.
5. Delete: `DELETE /conversations/{conversation_id}` soft-deletes.
6. Resume: `POST /conversations/{conversation_id}/resume` un-archives.
7. Search: `GET /conversations?q=...` filters by title and message content.

## API Integration

- `services/chat.service.ts` — `streamChatMessage`.
- `services/conversation.service.ts` — `list`, `get`, `create`, `update`, `archive`, `delete`, `search`.
- `services/birth-profile.service.ts` — `getProfile`, `getLatestProfileChart`.
- `hooks/use-chat.ts` — streaming, `sendMessage`, `stop`, `retry`, `regenerate`, `edit`, `delete`.

## Testing

- **Unit**: `chat.service.ts` SSE parsing, `useChat` state transitions.
- **Component**: `MessageItem`, `ExplainabilityPanel`, `ChatInput`, `ConversationList`.
- **Integration**: `POST /chat/{id}` with `MockProvider` returns SSE events and persists messages.
- **E2E**: Playwright navigates to `/chat`, sends a message, waits for streamed response, expands explainability.
