"""Integration tests for the reports API."""


def test_report_lifecycle(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "reports@example.com", "password": "password123", "name": "Reports"},
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "reports@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/reports",
        json={"title": "Full Horoscope", "category": "full_horoscope"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Full Horoscope"
    assert data["category"] == "full_horoscope"
    assert data["status"] == "pending"
    report_id = data["id"]

    response = client.get("/api/v1/reports", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(f"/api/v1/reports/{report_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Full Horoscope"

    response = client.patch(
        f"/api/v1/reports/{report_id}",
        json={"status": "ready", "file_url": "https://example.com/horoscope.pdf"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["file_url"] == "https://example.com/horoscope.pdf"

    response = client.delete(f"/api/v1/reports/{report_id}", headers=headers)
    assert response.status_code == 200

    response = client.get("/api/v1/reports", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_report_unauthorized(client):
    response = client.get("/api/v1/reports")
    assert response.status_code == 401
