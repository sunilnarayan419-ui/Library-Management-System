"""Top-level API router that mounts all v1 routers under /api/v1."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import ai, analytics, auth, books, circulation, health, recommendations, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(books.router)
api_router.include_router(users.router)
api_router.include_router(circulation.router)
api_router.include_router(analytics.router)
api_router.include_router(recommendations.router)
api_router.include_router(ai.router)
