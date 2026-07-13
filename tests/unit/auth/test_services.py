import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from divyadrishti.database import Base
from divyadrishti.services.authentication_service import AuthenticationService
from divyadrishti.services.birth_profile_service import BirthProfileService
from divyadrishti.services.conversation_service import ConversationService
from divyadrishti.services.preference_service import PreferenceService


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_authentication_service_register_and_login(db):
    auth = AuthenticationService(db)
    user = auth.register("service@example.com", "password123", "Service User")
    assert user.email == "service@example.com"
    tokens = auth.login("service@example.com", "password123")
    assert "access_token" in tokens


def test_birth_profile_service(db):
    auth = AuthenticationService(db)
    user = auth.register("profile@example.com", "password123", "Profile")
    service = BirthProfileService(db)
    profile = service.create(user.id, {"profile_name": "Self", "relationship": "self", "date_of_birth": "1990-01-01"})
    assert profile.profile_name == "Self"
    assert len(service.list(user.id)) == 1


def test_conversation_service(db):
    auth = AuthenticationService(db)
    user = auth.register("conv@example.com", "password123", "Conv")
    service = ConversationService(db)
    conv = service.create(user.id, {"title": "Q1"})
    assert conv.title == "Q1"
    service.add_message(conv.id, user.id, "user", "Hello")
    assert len(service.list(user.id)) == 1


def test_preference_service(db):
    auth = AuthenticationService(db)
    user = auth.register("pref@example.com", "password123", "Pref")
    service = PreferenceService(db)
    pref = service.update(user.id, {"preferred_language": "hi"})
    assert pref.preferred_language == "hi"
