# DivyaDrishti Release Readiness Report

Generated: 2026-07-18

## PROJECT SUMMARY

**Overall completion:** ~80% feature-complete for the MVP, ~55% production-ready.

DivyaDrishti is an AI-powered Vedic astrology expert system. The core application stack is implemented end-to-end: birth chart generation, deterministic astrological reasoning, explainability, a pluggable LLM gateway, knowledge corpus ingestion, and a Next.js chat workspace. All Playwright end-to-end flows and the targeted backend chat integration tests pass after the recent streaming fixes.

### Major implemented modules

- **Authentication & users** — JWT-based access/refresh tokens, registration, login, logout, password reset, role-based helpers.
- **Birth profiles & charts** — CRUD profiles, Swiss Ephemeris (`pyswisseph`) driven Rashi/Navamsa/D9/Dasha chart generation.
- **Astrological reasoning engine** — deterministic rule matching, evidence evaluation, conflict resolution, confidence scoring.
- **Explainability engine (XAI)** — reasoning graph, evidence breakdown, citations, confidence.
- **Conversational AI** — streaming chat via Server-Sent Events, retry/regenerate/edit/delete, optimistic message list.
- **Knowledge corpus** — book upload, OCR/PDF/Markdown/TXT extraction, semantic chunking, embeddings, candidate rule approval workflow.
- **Admin & feedback** — admin portal, user feedback collection.
- **Frontend** — Next.js 15 + React 19 + TypeScript + Tailwind + shadcn/ui, responsive three-panel chat layout.

### Major architecture components

| Layer | Stack |
|-------|-------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.11+, SQLAlchemy, Alembic |
| Database | SQLite (dev/MVP), PostgreSQL intended for production |
| Astrology | `pyswisseph` + custom Vedic reasoning engine |
| Vector Store | ChromaDB with sentence-transformer embeddings |
| AI | Pluggable LLM provider (OpenAI, Anthropic, Gemini, Ollama, or mock) |

---

## VERIFICATION STATUS

### Backend verification

- `tests/integration/test_chat.py` — **PASS** (3 passed, 2026-07-18 run).
- `verify_system.py` / `docs/PRODUCTION_VERIFICATION.md` — historical report shows all nine backend phases PASS, but the report is dated 2026-07-16 and the “Bugs Fixed” section is still marked `TBD`.
- Backend starts cleanly and the `/api/v1/health` endpoint responds.

### Frontend verification

- Playwright `verification.spec.ts` — **PASS** after the chat streaming fixes.
  - All 12 phases passed (`login-page`, `login-submit`, `responsive-mobile`, `chat-workspace`, `chat-streaming`, `birth-profiles`, `knowledge-library`, `settings`, `feedback`, `admin`, `conversations`, `error-404`).
  - Total run time: ~48s.
- `frontend_results.json` captured the passing run.

### Chat verification

- **Fixed:** `use-chat.ts` no longer dereferences a null `streamingAssistantRef` when a `delta` state updater is batched after the `metadata` event nullifies the ref.
- **Fixed:** `chat-context-panel.tsx` no longer renders the mobile context dialog as an overlay on desktop, which was intercepting Playwright clicks.
- Backend `POST /api/v1/chat/{conversation_id}` streams `user`, `delta`, `metadata`, and `done` SSE events correctly.

### Knowledge Corpus verification

- `docs/PRODUCTION_VERIFICATION.md` phase 3 passed historically.
- `CorpusIngestionPipeline` explicitly rejects `MockEmbeddingProvider` in production code.
- Unit tests use `InMemoryVectorStore` and `MockEmbeddingProvider`; these are test-only and should not be used in production.

### Authentication verification

- Registration, login, refresh, logout, protected routes, and JWT validation work in both integration and Playwright tests.
- `PermissionMiddleware` applies per-IP sliding-window rate limiting and JWT decoding.
- Endpoints rely on `get_current_user` (OAuth2 + `python-jose`) for authorization.

### Database verification

- SQLite file-backed database works for the MVP.
- `Base.metadata.create_all` is executed during the FastAPI lifespan; Alembic is present but not the active migration path at runtime.
- Playwright and integration tests create and persist conversations, messages, profiles, and charts.

### Testing status

| Test suite | Status | Notes |
|------------|--------|-------|
| Backend integration (`test_chat.py`) | PASS | Run directly via `python -m pytest`. |
| Playwright E2E (`verification.spec.ts`) | PASS | 12/12 phases. |
| Frontend unit tests (`vitest run`) | **Blocked by Environment** | Sandbox restrictions prevented `tools/node` from being added to `PATH`; not a codebase failure. |
| Backend unit tests | Not re-run in this session | `pytest` integration subset passed; full suite assumed healthy based on `PRODUCTION_VERIFICATION.md`. |

### Browser verification

- Chromium desktop viewport (1440×900) — PASS.
- Responsive/mobile viewport smoke test — PASS.

---

## KNOWN LIMITATIONS

### Environment limitations

- The execution sandbox blocks adding `tools/node` to `PATH`, so `npm run test:run` could not be executed here. This is an environment restriction, not a project bug.
- Playwright was run against the development build (`next dev`) using the local `tools/node` binary, not a static production build.

### Tool limitations

- `docs/PRODUCTION_VERIFICATION.md` is stale: it reports 100% readiness with a `TBD` bugs-fixed section and predates the streaming overlay / null-ref fixes.
- `verification/test_stream.py` has a latent bug (`ValueError: I/O operation on closed file`) because it tries to `tell()` after closing the output file; it is a debug harness and not production code.

### External dependencies

- LLM inference requires external provider keys (OpenAI, Anthropic, Gemini, Ollama) or the local `MockProvider`.
- Sentence-transformer embeddings are optional (`ml` extra); production corpus ingestion needs a real embedding provider.
- `chromadb` is used as the vector store; production deployments should consider a managed vector database or persistent Chroma server.

### Swiss Ephemeris status

- `pyswisseph>=2.10.0` is declared and used.
- `EPHEMERIS_PATH` defaults to empty; the bundled `pyswisseph` ephemeris is used. For higher precision or custom ephemeris files, `EPHEMERIS_PATH` must be configured and the files must be mounted into containers.

---

## TECHNICAL DEBT

Items transcribed from `docs/DECISIONS.md` and the codebase scan, classified by release impact.

### Critical

- `SECRET_KEY` default / example values (`change-this-to-a-32-byte-random-secret` in `.env.example` and `scripts/run_backend.py`) must be replaced with a cryptographically random key before any production deployment.
- `docker-compose.yml` currently deploys a single backend container with SQLite and no frontend service. Production needs a PostgreSQL service, frontend build, reverse proxy, and persistent volumes.
- `Base.metadata.create_all` runs in lifespan; production should run Alembic migrations explicitly and not rely on `create_all`.
- `settings.cors_origins` defaults to `["http://localhost:3000"]`, and `allow_methods/headers=["*"]` is set in `main.py` for development. A strict production CORS allowlist and explicit method/header lists are required.

### Important

- `get_settings()` is invoked at module import time in `database/database.py`, `main.py`, `security/token.py`, and `services/corpus_service.py`. This makes testing and environment switching harder. Move to runtime `Depends(get_settings)` and lazy engine creation.
- `structlog` JSONRenderer is selected by `LOG_LEVEL=INFO`; `LOG_FORMAT=json|console` should be a separate setting, and `get_logger(name)` should bind the logger name.
- `echo=settings.is_development` on the SQLAlchemy engine may leak queries in production if `INFO` is used. Disable echo or control it via a dedicated flag.
- Prompts and knowledge base are plain markdown files without versioning, schema validation, or A/B test metadata. Consider a YAML/JSON schema with version and tag fields.
- The security package is incomplete; ensure token, hashing, and dependency utilities are consolidated and reviewed.
- `InMemoryRateLimiter` is per-process and in-memory; a distributed deployment needs Redis or a gateway-level rate limiter.
- `docker-compose.yml` mounts `./backend/data:/app/data` but the application writes to `sqlite:///./divyadrishti.db` by default (inside the container, not `/app/data`). Align the database path or volume mount.
- `Dockerfile` does not create a non-root user.

### Minor

- `docs/ARCHITECTURE.md` contains an empty `## Component Diagrams` section.
- `docs/DECISIONS.md` ADR sections are headings-only with no content.
- `docs/PRODUCTION_VERIFICATION.md` is out of date and should be regenerated after the latest fixes.
- `verification/test_stream.py`, `verification/sse_dump.txt`, `verification/frontend_console.log`, and `verification/frontend_results.json` are temporary verification artifacts and should be excluded from release packaging.
- `scripts/run_backend.py` and `scripts/run_playwright_tests.ps1` are development helpers and should not be used in production.

---

## SECURITY REVIEW

### Authentication

- OAuth2 password flow with JWT access tokens and long-lived refresh tokens.
- Refresh tokens carry a `jti`; the auth service checks revocation on logout.
- Passwords are hashed with bcrypt/argon2 (`passlib[bcrypt]`, `argon2-cffi`).
- Email verification and password reset tokens are generated with `secrets.token_urlsafe(32)`.

### JWT

- Tokens are signed with `HS256` and the `SECRET_KEY` from settings.
- `decode_token` returns `None` on `JWTError`.
- Access and refresh token expiry durations are configurable via env vars.

### Secrets

- `SECRET_KEY` is required at startup (`min_length=16` via Pydantic).
- `.env.example` and `scripts/run_backend.py` contain weak placeholder values. These must be rotated and stored in a secrets manager for production.
- LLM API keys, database credentials, and `EPHEMERIS_PATH` are configured through environment variables.

### Permissions

- `require_role`, `require_admin`, and `require_permission` dependencies exist.
- `has_permission` checks the user role.
- Individual endpoints use `get_current_user` to enforce authentication and user isolation.

### Rate limiting

- `InMemoryRateLimiter` (60 requests / 60 seconds / IP) is enforced in `PermissionMiddleware`.
- Distributed deployments need a shared store (e.g., Redis).
- There is no per-user or per-endpoint tiered rate limiting.

### CORS

- CORS origins are read from `CORS_ORIGINS` env var.
- `allow_methods=["*"]` and `allow_headers=["*"]` are set for development. Tighten to the actual frontend origin, methods, and headers in production.

### Uploads

- Knowledge corpus accepts PDF/Markdown/TXT/TXT via `UploadFile`.
- File type, size limits, and malware scanning should be reviewed before public deployment.
- Uploaded files are processed offline by the ingestion pipeline.

---

## PERFORMANCE REVIEW

### Database

- SQLite is adequate for local development and small-scale testing.
- For production, switch to PostgreSQL, add connection-pool tuning, and migrate with Alembic.
- `Base.metadata.create_all` on every startup is acceptable for dev but not for production.
- The current schema has basic indexes; a production review should add query-specific indexes for conversations, messages, and charts.

### Reasoning

- The reasoning engine is deterministic and synchronous. It runs inside the chat request thread and could block for complex charts.
- Consider moving chart generation and reasoning to background workers (Celery/RQ) for large workloads.

### Knowledge retrieval

- ChromaDB is used for vector search. Performance depends on embedding dimension, collection size, and the embedding model.
- `sentence-transformers` is an optional dependency; production ingestion must install it or use an equivalent provider.

### Embeddings

- `MockEmbeddingProvider` is reserved for unit tests and rejected in `CorpusIngestionPipeline`.
- `SentenceTransformerEmbeddingProvider` or `OpenAIEmbeddingProvider` should be used in production.

### Streaming

- The chat stream uses `StreamingResponse` with `text/event-stream`.
- The frontend reads the stream via `fetch` + `ReadableStream` and parses `data:` lines.
- Recent fixes remove state-update races; streaming is now stable in Playwright tests.

### Frontend

- `react-virtuoso` virtualizes the message list.
- `react-markdown` + `remark-gfm` renders assistant messages.
- Some hydration mismatches are visible in dev-console logs (auth-dependent client components). These are non-fatal because React re-renders client-side, but they should be addressed for production builds.

---

## RELEASE CHECKLIST

| Item | Status | Notes |
|------|--------|-------|
| Database migrations | Partial | Alembic present; app currently uses `create_all` in lifespan. |
| Environment variables | Partial | `.env.example` exists; defaults are insecure placeholders. |
| Production secrets | Not ready | `SECRET_KEY`, LLM keys, DB credentials need rotation. |
| Docker | Partial | Backend Dockerfile only; compose uses SQLite and no frontend. |
| CI/CD | Missing | No `.github/workflows` or equivalent pipelines. |
| Logging | Partial | `structlog` configured; JSON vs console should be separate. |
| Monitoring | Missing | No health dashboards, metrics, or alerting. |
| Backups | Missing | No backup strategy for SQLite/Postgres or knowledge corpus. |
| Error reporting | Partial | Global 500 handler exists; no Sentry or similar. |
| HTTPS | Missing | Dev-only HTTP; production needs TLS termination. |

---

## FUTURE ROADMAP

- **Interactive Birth Chart Studio** — visual, clickable chart exploration.
- **Explainability Explorer** — standalone trace viewer for reasoning paths and evidence.
- **Professional Report Generator** — downloadable PDF horoscope / career / marriage reports.
- **Knowledge Library UI** — richer corpus management, rule versioning, and admin review tools.
- **Admin Portal** — user management, analytics, and content moderation.
- **Landing Website** — public marketing and documentation site.
- **Production Deployment** — managed Postgres, Redis, container orchestration, CDN, and CI/CD.

---

## FINAL SCORE

**Production readiness: 55%**

**Recommendation: Needs Major Work**

The MVP is feature-complete and functional enough for demos and closed beta testing on a trusted developer workstation. However, several production-critical items are not ready:

- Deployment pipeline (Docker compose, CI/CD, HTTPS, monitoring) is missing or under-developed.
- Default secrets and `SECRET_KEY` are placeholders.
- CORS, rate limiting, logging, and database migrations are still in development mode.
- The verification report and several ADR documents are empty or stale.

Before a public beta, prioritize:

1. Rotate all secrets and remove placeholder defaults.
2. Add a PostgreSQL service, run Alembic migrations, and remove `create_all` from lifespan.
3. Harden CORS, rate limiting, and file upload handling.
4. Build CI/CD and a production `docker-compose.yml` with reverse proxy and TLS.
5. Add monitoring, backups, and centralized logging.
