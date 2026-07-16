import os

# Ensure configuration is set before any application modules are imported.
os.environ.setdefault("SECRET_KEY", "test-secret-key-1234567890")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
# Add email configuration for tests (using localhost as a safe default)
os.environ.setdefault("EMAIL_HOST", "localhost")
os.environ.setdefault("EMAIL_PORT", "25")
os.environ.setdefault("EMAIL_USERNAME", "")
os.environ.setdefault("EMAIL_PASSWORD", "")
os.environ.setdefault("EMAIL_FROM", "test@example.com")
# Use mock LLM provider for tests to avoid external API calls.
os.environ.setdefault("LLM_PROVIDER", "mock")

import pytest
from fastapi.testclient import TestClient

from divyadrishti.database import Base, SessionLocal, engine, get_db
from divyadrishti.main import app


def override_get_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)
