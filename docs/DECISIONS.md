# Architecture Decision Records

## ADR-001: Tech Stack

## ADR-002: Database Choice

## ADR-003: LLM Provider Strategy

## ADR-004: Reasoning Trace Format

## ADR-005: Ayanamsa and House System

## ADR-006: Authentication Method

## Open Questions

## Technical Debt

### Backend Package Boundary
- `core` and `models` packages overlap conceptually. We need a clear convention: `models` for persistence, `core` for domain models/events.
- `config` package is a single module; consider splitting into `settings.py` and `dependencies.py` for FastAPI injection.

### Settings Lifecycle
- `get_settings()` is called at module import time in `database/database.py` and `main.py`.
- This creates engine creation during import, which makes testing and environment switching harder.
- Recommendation: use FastAPI dependency `Depends(get_settings)` for runtime settings and lazy engine creation.

### Database
- SQLite is used for MVP; migration is via Alembic.
- `echo=settings.is_development` may leak sensitive queries in production.
- Connection pool settings for PostgreSQL are not yet defined.
- `Base.metadata.create_all(bind=engine)` in `lifespan` is fine for MVP but should be replaced by Alembic in production.

### Logging
- `structlog` JSONRenderer is chosen for production but `INFO` level picks JSON while `DEBUG` picks console.
- Better to use an env var `LOG_FORMAT=json|console` independent of `LOG_LEVEL`.
- `get_logger(name)` currently ignores `name` due to `structlog` defaults; ensure `structlog.get_logger(name)` binds the name.

### Prompts and Knowledge
- Prompts and knowledge base are markdown files; versioning and runtime loading are not yet designed.
- Consider a YAML/JSON schema with versioning, tags, and A/B test metadata.

### Security
- `SECRET_KEY` is required at startup. Missing key currently causes `pydantic` error on import, which prevents running health checks.
- `SECRET_KEY` should be validated at app startup, not at module import.
- Security package is empty; need token, hashing, and dependency utilities.

### Frontend / Backend Integration
- CORS is configured from `.env` but allows all methods/headers in development.
- Define stricter production CORS rules and domain allowlist.

### Containerization
- `docker-compose.yml` mounts `./backend/data` for SQLite but not `.env`.
- Production should use a separate PostgreSQL service and secrets management.
- Dockerfile does not create a non-root user; recommended for production.
