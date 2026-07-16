# DivyaDrishti

An AI-powered Vedic Astrology (Jyotish) Expert System that combines traditional astrological principles with modern AI to deliver **explainable**, **personalized**, and **conversational** astrological insights.

## What is DivyaDrishti?

DivyaDrishti generates accurate Vedic birth charts, reasons about them using a deterministic rule-evaluation engine grounded in classical texts, and then uses an LLM purely to phrase the answer in natural, conversational language — the astrology and reasoning are never delegated to the LLM itself. Every answer can be traced back to the exact rule, chart factor, and classical reference that produced it.

Key capabilities:
- **Birth Chart Generation** — Rashi/Navamsa charts, planetary positions, houses, yogas, and Vimshottari dashas computed with the Swiss Ephemeris (`pyswisseph`).
- **Astrological Reasoning Engine** — a deterministic, explainable engine (question analysis → rule matching → evidence evaluation → conflict resolution → confidence scoring) that never fabricates conclusions.
- **Knowledge Corpus** — administrators can upload classical texts (PDF/scanned/Markdown/TXT, multi-language with OCR fallback); the system extracts chapter/verse/page-aware semantic chunks, embeds them, and proposes candidate rules for human review before they ever influence reasoning.
- **Explainability Engine (XAI)** — every response ships with a traceable reasoning graph, supporting/conflicting evidence, confidence breakdown, and classical citations.
- **Conversational AI Layer** — a pluggable, provider-agnostic LLM gateway (OpenAI, Anthropic, Gemini, Ollama, or a local mock) turns structured reasoning into natural-language, multilingual responses — it only narrates, it never decides.
- **User & Profile Management** — authentication, multiple birth profiles, conversation history, feedback, and an admin review workflow for knowledge quality.

## Architecture

| Layer | Stack |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.12+, SQLAlchemy, Alembic |
| Database | SQLite (development/MVP), PostgreSQL (production) |
| Astrology Engine | `pyswisseph` (Swiss Ephemeris) + custom Vedic reasoning logic |
| Knowledge/Vector Store | ChromaDB, sentence-transformers embeddings |
| AI | Pluggable LLM provider (OpenAI, Anthropic, Gemini, Ollama, or mock) |

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full system design, and the rest of the [`docs/`](docs) directory for deep dives into each subsystem (reasoning engine, explainability, knowledge base, chat, frontend, etc.).

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- A C/C++ build toolchain if `pyswisseph` needs to compile from source on your platform (prebuilt wheels are available for most common platforms/Python versions).

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/macOS

pip install -e .
cp .env.example .env        # then set SECRET_KEY (and any LLM provider API keys)

alembic upgrade head
uvicorn divyadrishti.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` (interactive docs at `/docs`).

Useful backend commands:
```bash
pytest          # run tests
ruff check .     # lint
mypy .           # type-check
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

The app will be available at `http://localhost:3000`.

Useful frontend commands:
```bash
npm run build      # production build
npm run lint        # lint
npm run test:run    # unit tests (Vitest)
npm run test:e2e    # end-to-end tests (Playwright)
```

### Docker (backend + dependencies)

```bash
docker-compose up --build
```

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system-wide architecture
- [`docs/REASONING_ENGINE.md`](docs/REASONING_ENGINE.md) — astrological reasoning engine
- [`docs/EXPLAINABILITY_ENGINE.md`](docs/EXPLAINABILITY_ENGINE.md) — explainability/XAI engine
- [`docs/KNOWLEDGE_BASE.md`](docs/KNOWLEDGE_BASE.md) — knowledge base and rule storage
- [`docs/DOCUMENT_PROCESSING.md`](docs/DOCUMENT_PROCESSING.md) — book ingestion pipeline
- [`docs/CHAT_ARCHITECTURE.md`](docs/CHAT_ARCHITECTURE.md) — conversational AI layer
- [`docs/ADMIN_GUIDE.md`](docs/ADMIN_GUIDE.md) — administrator workflows
- [`docs/API.md`](docs/API.md) — API reference
