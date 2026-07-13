"""Integration tests for chat streaming."""

import json


def _register_and_login(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "chat@example.com", "password": "password123", "name": "Chat"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "chat@example.com", "password": "password123"},
    )
    return login.json()["access_token"]


def test_chat_stream_creates_messages(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/conversations",
        json={"title": "Marriage question", "domain": "marriage"},
        headers=headers,
    )
    assert response.status_code == 201
    conversation_id = response.json()["id"]

    events = []
    with client.stream(
        "POST",
        f"/api/v1/chat/{conversation_id}",
        json={"content": "Will I marry?"},
        headers=headers,
    ) as resp:
        assert resp.status_code == 200
        for line in resp.iter_lines():
            if line and line.startswith("data: "):
                events.append(json.loads(line[6:]))

    event_types = [e["event"] for e in events]
    assert "user" in event_types
    assert "delta" in event_types
    assert "metadata" in event_types
    assert "done" in event_types

    response = client.get(f"/api/v1/conversations/{conversation_id}", headers=headers)
    assert response.status_code == 200
    messages = response.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["ai_response_json"]
    assert messages[1]["reasoning_result"]
    assert messages[1]["explainability_report"]


def test_chat_conversation_not_found(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/chat/99999",
        json={"content": "Hello"},
        headers=headers,
    )
    assert response.status_code == 404


def test_conversations_search(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/conversations",
        json={"title": "Marriage question", "domain": "marriage"},
        headers=headers,
    )

    response = client.get("/api/v1/conversations?q=marriage", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get("/api/v1/conversations?q=absent", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0
