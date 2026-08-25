"""End-to-end integration test covering the exact workflow called out in
the modernization brief:

    Create user -> Create book -> Create copy -> Issue -> Verify
    unavailable -> Return -> Verify available
"""
from __future__ import annotations

from tests.conftest import auth_headers


def test_full_circulation_workflow(client):
    # Create an admin (to manage books/circulation) and a member (to borrow).
    client.post(
        "/api/v1/auth/register",
        json={"name": "Librarian", "email": "libr@lms.example", "password": "Password123", "role": "LIBRARIAN"},
    )
    client.post(
        "/api/v1/auth/register",
        json={"name": "Reader", "email": "reader@lms.example", "password": "Password123", "role": "MEMBER"},
    )
    staff_headers = auth_headers(client, "libr@lms.example", "Password123")
    member_resp = client.get("/api/v1/auth/me", headers=auth_headers(client, "reader@lms.example", "Password123"))
    member_id = member_resp.json()["data"]["id"]

    # Create book with a single copy.
    resp = client.post(
        "/api/v1/books",
        json={"title": "Domain-Driven Design", "author": "Eric Evans", "category": "Software", "initial_copies": 1},
        headers=staff_headers,
    )
    assert resp.status_code == 201
    book = resp.json()["data"]
    assert book["available_copies"] == 1

    # Issue the only copy.
    resp = client.post(
        "/api/v1/circulation/issue",
        json={"book_id": book["id"], "member_id": member_id},
        headers=staff_headers,
    )
    assert resp.status_code == 200, resp.text
    loan = resp.json()["data"]
    assert loan["status"] == "ACTIVE"

    # Verify book now shows zero available copies.
    resp = client.get(f"/api/v1/books/{book['id']}", headers=staff_headers)
    assert resp.json()["data"]["available_copies"] == 0

    # A second issue attempt must fail — book is unavailable.
    resp = client.post(
        "/api/v1/circulation/issue",
        json={"book_id": book["id"], "member_id": member_id},
        headers=staff_headers,
    )
    assert resp.status_code == 409

    # Return the book.
    resp = client.post("/api/v1/circulation/return", json={"loan_id": loan["id"]}, headers=staff_headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "RETURNED"

    # Verify the copy is available again.
    resp = client.get(f"/api/v1/books/{book['id']}", headers=staff_headers)
    assert resp.json()["data"]["available_copies"] == 1

    # A second return of the same loan must fail.
    resp = client.post("/api/v1/circulation/return", json={"loan_id": loan["id"]}, headers=staff_headers)
    assert resp.status_code == 409
