# DivyaDrishti Project Guide

## Commands

### Backend
- `cd backend`
- **Use Python 3.11 or 3.12** for `pyswisseph` wheel compatibility (Python 3.14 requires source compilation)
- `python -m venv .venv` (on Windows with multiple versions: `py -3.11 -m venv .venv`)
- `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/macOS)
- `pip install -e .`
- `cp .env.example .env` and set `SECRET_KEY`
- `alembic upgrade head`
- `start_backend.ps1` (Windows) or `./start_backend.sh` (Linux/macOS) to enforce Python 3.11/3.12
- `uvicorn divyadrishti.main:app --reload --host 0.0.0.0 --port 8000`
- `pytest` (from project root)
- `ruff check .` (from backend/)
- `mypy .` (from backend/)

### Frontend
- `cd frontend`
- `cp .env.example .env.local`
- `npm install`
- `npm run dev`
- `npm run build`
- `npm run lint`
- `npm run test:run`
- `npm run test:e2e`

### Docker
- `docker-compose up --build`

## Architecture
- Backend: FastAPI + Python + SQLAlchemy
- Frontend: Next.js + TypeScript + Tailwind + shadcn/ui
- Database: SQLite (MVP), PostgreSQL (production)
- AI: pluggable LLM provider
- Astrology: pyswisseph + custom reasoning engine
