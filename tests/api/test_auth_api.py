from __future__ import annotations


def test_register_and_login(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@lms.example", "password": "Password123", "role": "MEMBER"},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["data"]["email"] == "alice@lms.example"

    resp = client.post("/api/v1/auth/login", json={"email": "alice@lms.example", "password": "Password123"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["tokens"]["access_token"]

    token = body["data"]["tokens"]["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["data"]["email"] == "alice@lms.example"


def test_login_with_wrong_password_returns_401(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Bob", "email": "bob@lms.example", "password": "Password123", "role": "MEMBER"},
    )
    resp = client.post("/api/v1/auth/login", json={"email": "bob@lms.example", "password": "wrong"})
    assert resp.status_code == 401
    assert resp.json()["success"] is False


def test_protected_endpoint_without_token_returns_401(client):
    resp = client.get("/api/v1/books")
    assert resp.status_code == 401


def test_duplicate_email_registration_returns_409(client):
    payload = {"name": "Carl", "email": "carl@lms.example", "password": "Password123", "role": "MEMBER"}
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409
