"""Deterministic, dependency-free provider used by default and in tests.

This intentionally reproduces (and slightly generalizes) the keyword
knowledge-base approach from the legacy `/api/chat` endpoint, so the
"AI librarian" keeps working with zero external dependencies and zero
API cost out of the box.
"""
from __future__ import annotations

import re

KNOWLEDGE_BASE: dict[str, list[str]] = {
    "sherlock": ["Sherlock Holmes", "detective", "mystery"],
    "holmes": ["Sherlock Holmes"],
    "detective": ["Sherlock Holmes", "Agatha Christie"],
    "dinosaur": ["Jurassic Park"],
    "jurassic": ["Jurassic Park"],
    "vatican": ["Angels & Demons"],
    "murder": ["Crime and Punishment", "Sherlock Holmes"],
    "napoleon": ["Animal Farm"],
    "wizard": ["Harry Potter"],
    "magic": ["Harry Potter"],
    "hobbit": ["Lord of the Rings"],
    "ring": ["Lord of the Rings"],
    "economics": ["Wealth of Nations", "Freakonomics"],
    "physics": ["Physics & Philosophy", "Tao of Physics"],
    "feynman": ["Surely You're Joking Mr Feynman"],
    "india": ["Discovery of India"],
    "gandhi": ["My Experiments with Truth"],
    "war": ["War and Peace", "Farewell to Arms"],
    "vampire": ["Twilight", "Dracula"],
}


class MockProvider:
    """Keyword-matching provider — no network calls, always available."""

    name = "mock"

    def generate(self, prompt: str, *, context: str | None = None) -> str:
        message = prompt.lower()
        tokens = re.findall(r"\w+", message)

        related: list[str] = []
        for token in tokens:
            for key, values in KNOWLEDGE_BASE.items():
                if key in token or token in key:
                    related.extend(values)

        related = list(dict.fromkeys(related))  # dedupe, preserve order

        if context:
            return f"Based on your library's catalog, here's what I found: {context}"
        if related:
            return "You might be interested in: " + ", ".join(related[:3]) + "."
        return "I'm not sure which book you mean. Try mentioning a title, author, or genre keyword!"
