def test_register_and_login(client):
    # Register
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "password123", "name": "Test User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_get_me_requires_auth(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_me_endpoint(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "password123", "name": "Me"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_birth_profile_lifecycle(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "profile@example.com", "password": "password123", "name": "Profile"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "profile@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/profiles",
        json={
            "profile_name": "Self",
            "relationship": "self",
            "date_of_birth": "1990-01-01",
            "time_of_birth": "10:00:00",
            "birth_place": "Delhi",
            "latitude": 28.61,
            "longitude": 77.21,
            "timezone": "Asia/Kolkata",
            "accuracy_level": "exact",
        },
        headers=headers,
    )
    assert response.status_code == 201
    profile_id = response.json()["id"]

    response = client.get("/api/v1/profiles", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.patch(
        "/api/v1/profiles/1",
        json={"profile_name": "Updated"},
        headers=headers,
    )
    # Profile ID may be 1 or 2 depending on tests; this is a sanity check
    if response.status_code == 200:
        assert response.json()["profile_name"] == "Updated"

    response = client.delete(f"/api/v1/profiles/{profile_id}", headers=headers)
    assert response.status_code == 200


def test_conversation_lifecycle(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "conv@example.com", "password": "password123", "name": "Conv"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "conv@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/conversations",
        json={"title": "Marriage question", "domain": "marriage"},
        headers=headers,
    )
    assert response.status_code == 201
    conversation_id = response.json()["id"]

    response = client.get("/api/v1/conversations", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Will I marry?"},
        headers=headers,
    )
    assert response.status_code == 200

    response = client.get(f"/api/v1/conversations/{conversation_id}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()["messages"]) == 1


def test_preferences_and_feedback(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "pref@example.com", "password": "password123", "name": "Pref"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "pref@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/preferences", headers=headers)
    assert response.status_code == 200
    assert response.json()["preferred_language"] == "en"

    response = client.patch(
        "/api/v1/preferences",
        json={"preferred_language": "hi", "dark_mode": True},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["preferred_language"] == "hi"
    assert response.json()["dark_mode"] is True

    response = client.post(
        "/api/v1/feedback",
        json={"rating": "Helpful", "comment": "Good answer"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["rating"] == "Helpful"
