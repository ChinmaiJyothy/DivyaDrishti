from divyadrishti.security import hash_password, verify_password
from divyadrishti.security.token import create_access_token, create_refresh_token, decode_token


def test_password_hashing():
    hashed = hash_password("my-secret-password")
    assert verify_password("my-secret-password", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token():
    token = create_access_token("123")
    payload = decode_token(token)
    assert payload["sub"] == "123"
    assert payload["type"] == "access"


def test_refresh_token():
    token, jti = create_refresh_token("123")
    payload = decode_token(token)
    assert payload["sub"] == "123"
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti
