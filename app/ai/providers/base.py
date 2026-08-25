"""LLM provider abstraction.

New AI providers (OpenAI, Anthropic, a local model, etc.) implement this
Protocol and are selected at runtime via the `AI_PROVIDER` setting, so the
rest of the application never hardcodes a specific vendor SDK.
"""
from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    name: str

    def generate(self, prompt: str, *, context: str | None = None) -> str:
        """Return a text completion for the given prompt."""
        ...
