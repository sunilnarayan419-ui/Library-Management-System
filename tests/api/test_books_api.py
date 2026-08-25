from __future__ import annotations

from tests.conftest import auth_headers


def test_member_cannot_create_book(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Mem", "email": "mem@lms.example", "password": "Password123", "role": "MEMBER"},
    )
    headers = auth_headers(client, "mem@lms.example", "Password123")
    resp = client.post("/api/v1/books", json={"title": "X", "author": "Y"}, headers=headers)
    assert resp.status_code == 403


def test_admin_can_create_and_list_books(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Admin", "email": "admin2@lms.example", "password": "Password123", "role": "ADMIN"},
    )
    headers = auth_headers(client, "admin2@lms.example", "Password123")

    resp = client.post(
        "/api/v1/books",
        json={"title": "The Pragmatic Programmer", "author": "Hunt & Thomas", "category": "Software", "initial_copies": 2},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    book = resp.json()["data"]
    assert book["total_copies"] == 2
    assert book["available_copies"] == 2

    resp = client.get("/api/v1/books?search=Pragmatic", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["meta"]["total"] == 1


def test_duplicate_isbn_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={"name": "Admin3", "email": "admin3@lms.example", "password": "Password123", "role": "ADMIN"},
    )
    headers = auth_headers(client, "admin3@lms.example", "Password123")
    payload = {"title": "Book A", "author": "Author A", "isbn": "111-222"}
    r1 = client.post("/api/v1/books", json=payload, headers=headers)
    assert r1.status_code == 201
    r2 = client.post("/api/v1/books", json={**payload, "title": "Book B"}, headers=headers)
    assert r2.status_code == 409
