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
10. `POST /chat/{conversation_id}` accepts an optional `message_id` to retry, regenerate, or edit an existing user message; the service reuses the user message, updates its content if changed, and deletes any assistant messages after it.
11. `DELETE /conversations/{conversation_id}/messages/{message_id}` deletes a message and all messages after it.

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
app/(dashboard)/
├── layout.tsx               # Chooses ChatLayout for chat routes, DashboardLayout otherwise
├── ask/page.tsx             # Creates a conversation and redirects to /chat/{id}?question=...
├── chat/page.tsx            # Welcome screen that redirects to /ask?question=...
├── chat/[id]/page.tsx       # Renders ChatWorkspace inside ChatLayout

components/chat/
├── chat-layout.tsx          # ChatLayout: sidebar + main + right context panel
├── chat-context.tsx         # ChatContextProvider + useChatContext
├── chat-workspace.tsx       # Chat header, message list, input, suggestions
├── chat-header.tsx          # Title, rename, archive, delete, open context panel
├── conversation-sidebar.tsx # Searchable conversation list with group/pin/archive
├── conversation-item.tsx    # Single conversation row with actions
├── new-chat-button.tsx      # Button to create a new conversation
├── message-list.tsx         # Virtualized list (react-virtuoso)
├── message-item.tsx         # Message bubble + explainability panel
├── message-bubble.tsx       # Markdown rendering with code blocks
├── message-actions.tsx      # Copy, edit, delete, retry, regenerate, stop
├── streaming-message.tsx    # Inline assistant message while streaming
├── chat-input.tsx           # Textarea with send/stop and quick prompts
├── chat-context-panel.tsx   # Active message details + suggested follow-ups
├── explainability-panel.tsx # Expandable explainability inside message item
├── reasoning-graph.tsx      # Graph visualization of reasoning
├── confidence-breakdown.tsx # Confidence score breakdown
├── suggested-questions.tsx  # Follow-up question chips
├── welcome-chat.tsx         # Empty state with example prompts
└── typing-indicator.tsx     # Animated dots shown while waiting
```

### State

- `useChat` hook in `frontend/hooks/use-chat.ts` owns:
  - `conversationId`
  - `messages` (local optimistic list)
  - `isStreaming` / `isLoading` / `error`
  - `sendMessage(content, messageId?)` supports new messages and retry/regenerate/edit
  - `stop`, `retry`, `regenerate`, `editMessage`, `deleteMessage` operations
  - Invalidates the `conversation` query after each completed/failed stream to keep the server and UI in sync
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

- `services/chat.service.ts` — `streamChatMessage` (supports `message_id` for retry/edit/regenerate).
- `services/conversation.service.ts` — `list`, `get`, `create`, `update`, `archive`, `delete`, `search`, `deleteMessage`.
- `services/birth-profile.service.ts` — `getProfile`, `getLatestProfileChart`.
- `hooks/use-chat.ts` — streaming, `sendMessage`, `stop`, `retry`, `regenerate`, `edit`, `delete`.

## Testing

- **Unit**: `chat.service.ts` SSE parsing, `useChat` state transitions.
- **Component**: `MessageItem`, `ExplainabilityPanel`, `ChatInput`, `ConversationList`.
- **Integration**: `POST /chat/{id}` with `MockProvider` returns SSE events and persists messages.
- **E2E**: Playwright navigates to `/chat`, sends a message, waits for streamed response, expands explainability.
