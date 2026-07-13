"""Integration tests for the knowledge library API (admin only)."""

from io import BytesIO

from divyadrishti.models import Role, User
from divyadrishti.security.password import hash_password


def _create_admin_user(client, db):
    role = Role(name="admin")
    db.add(role)
    db.commit()

    user = User(
        email="admin@example.com",
        name="Admin",
        hashed_password=hash_password("password123"),
        role_id=role.id,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.close()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    return login.json()["access_token"]


def test_knowledge_admin_only(client):
    response = client.get("/api/v1/knowledge")
    assert response.status_code == 401

    response = client.get("/api/v1/books")
    assert response.status_code == 401


def test_knowledge_lifecycle(client, db):
    token = _create_admin_user(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/knowledge", headers=headers)
    assert response.status_code == 200
    overview = response.json()
    assert overview["books_count"] == 0
    assert overview["versions_count"] == 0

    response = client.get("/api/v1/books", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/api/v1/knowledge/versions", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    file = BytesIO(b"book content")
    response = client.post(
        "/api/v1/books",
        files={"file": ("test_book.pdf", file, "application/pdf")},
        data={"title": "Test Book", "author": "Author", "language": "en"},
        headers=headers,
    )
    assert response.status_code == 201
    book = response.json()
    assert book["title"] == "Test Book"
    assert book["file_name"] == "test_book.pdf"
    book_id = book["id"]

    response = client.get("/api/v1/books", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get("/api/v1/knowledge", headers=headers)
    assert response.status_code == 200
    assert response.json()["books_count"] == 1

    response = client.delete(f"/api/v1/books/{book_id}", headers=headers)
    assert response.status_code == 200

    response = client.get("/api/v1/books", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_non_admin_cannot_upload(client, db):
    role = Role(name="user")
    db.add(role)
    db.commit()

    user = User(
        email="user@example.com",
        name="User",
        hashed_password=hash_password("password123"),
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.close()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    file = BytesIO(b"book content")
    response = client.post(
        "/api/v1/books",
        files={"file": ("test_book.pdf", file, "application/pdf")},
        data={"title": "Test Book"},
        headers=headers,
    )
    assert response.status_code == 403
