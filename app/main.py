"""FastAPI application factory / entrypoint.

Run locally with:
    uvicorn app.main:app --reload
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware, register_exception_handlers
from app.database.base import Base
from app.database.session import engine


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(debug=settings.app_debug)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Production-grade Library Management Platform API (v5).",
        docs_url="/swagger",
        redoc_url="/redoc",
        openapi_url="/api/v1/openapi.json",
    )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    @app.on_event("startup")
    def on_startup() -> None:
        # For SQLite/dev convenience, ensure tables exist even before Alembic
        # migrations are run. In production, `alembic upgrade head` is the
        # source of truth for schema changes (see docs/database.md).
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
