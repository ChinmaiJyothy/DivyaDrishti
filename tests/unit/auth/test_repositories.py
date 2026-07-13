import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from divyadrishti.database import Base
from divyadrishti.repositories import BirthProfileRepository, ConversationRepository, UserRepository
from divyadrishti.services.authentication_service import AuthenticationService


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


def test_user_repository_get_by_email(db):
    auth = AuthenticationService(db)
    auth.register("repo@example.com", "password123", "Repo")
    repo = UserRepository(db)
    user = repo.get_by_email("repo@example.com")
    assert user is not None
    assert user.email == "repo@example.com"


def test_birth_profile_repository(db):
    auth = AuthenticationService(db)
    user = auth.register("bp@example.com", "password123", "BP")
    repo = BirthProfileRepository(db)
    from divyadrishti.models import BirthProfile

    profile = repo.create(BirthProfile(user_id=user.id, profile_name="Self", relationship="self", date_of_birth="1990-01-01"))
    assert profile.id is not None
    assert repo.get_by_id(profile.id, user.id) == profile


def test_conversation_repository(db):
    auth = AuthenticationService(db)
    user = auth.register("cr@example.com", "password123", "CR")
    repo = ConversationRepository(db)
    from divyadrishti.models import Conversation

    conv = repo.create(Conversation(user_id=user.id, title="Q"))
    assert repo.get_by_id(conv.id, user.id) == conv

    from divyadrishti.models.conversation import Message

    msg = repo.add_message(Message(conversation_id=conv.id, role="user", content="Hello"))
    assert msg.conversation_id == conv.id
