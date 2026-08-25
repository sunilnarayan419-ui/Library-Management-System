"""AI Librarian service — resolves the configured provider and answers
member questions using the current book catalog as grounding context.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai.providers.base import LLMProvider
from app.ai.providers.mock_provider import MockProvider
from app.core.config import Settings, get_settings
from app.models.book import Book


def get_provider(settings: Settings | None = None) -> LLMProvider:
    settings = settings or get_settings()
    if settings.ai_provider == "anthropic" and settings.ai_api_key:
        from app.ai.providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider(api_key=settings.ai_api_key, model=settings.ai_model)
    return MockProvider()


class AILibrarian:
    def __init__(self, db: Session, provider: LLMProvider | None = None):
        self.db = db
        self.provider = provider or get_provider()

    def _matching_catalog_context(self, message: str, limit: int = 5) -> str | None:
        message_lower = message.lower()
        books = self.db.query(Book).all()
        matches = [
            b for b in books
            if message_lower in b.title.lower() or message_lower in b.author.lower()
        ]
        if not matches:
            return None
        lines = [f"- {b.title} by {b.author} ({b.category or 'general'})" for b in matches[:limit]]
        return "\n".join(lines)

    def chat(self, message: str) -> str:
        if not message.strip():
            return "I'm listening! Ask me about any book, character, or topic."
        context = self._matching_catalog_context(message)
        return self.provider.generate(message, context=context)
