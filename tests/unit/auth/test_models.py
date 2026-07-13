from divyadrishti.models import User


def test_user_model():
    user = User(email="test@example.com", name="Test", hashed_password="x", role_id=1)
    assert user.email == "test@example.com"
    assert user.name == "Test"
    assert user.__tablename__ == "users"
