from contextlib import asynccontextmanager

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import divyadrishti.models  # noqa: F401
from divyadrishti.api.v1.routers import auth, birth_profiles, conversations, feedback, health, preferences, users
from divyadrishti.config import get_settings
from divyadrishti.database import Base, engine
from divyadrishti.security.middleware import PermissionMiddleware
from divyadrishti.utils import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown complete")


app = FastAPI(
    title="DivyaDrishti API",
    description="AI-powered Vedic Astrology Expert System",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(PermissionMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(birth_profiles.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(preferences.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )
