# DivyaDrishti Project Guide

## Commands

### Backend
- `cd backend`
- `python -m venv .venv`
- `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/macOS)
- `pip install -e .`
- `cp .env.example .env` and set `SECRET_KEY`
- `uvicorn divyadrishti.main:app --reload --host 0.0.0.0 --port 8000`
- `alembic upgrade head`
- `pytest`
- `ruff check .`
- `mypy .`

### Docker
- `docker-compose up --build`

## Architecture
- Backend: FastAPI + Python + SQLAlchemy
- Frontend: Next.js + TypeScript + Tailwind + shadcn/ui
- Database: SQLite (MVP), PostgreSQL (production)
- AI: pluggable LLM provider
- Astrology: pyswisseph + custom reasoning engine
