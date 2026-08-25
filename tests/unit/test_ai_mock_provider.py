from __future__ import annotations

from app.ai.providers.mock_provider import MockProvider


def test_mock_provider_finds_related_titles():
    provider = MockProvider()
    reply = provider.generate("tell me about wizards and magic")
    assert "Harry Potter" in reply


def test_mock_provider_uses_catalog_context_when_present():
    provider = MockProvider()
    reply = provider.generate("dune", context="- Dune by Frank Herbert (Sci-Fi)")
    assert "Dune" in reply


def test_mock_provider_falls_back_gracefully():
    provider = MockProvider()
    reply = provider.generate("asdkjfhaskjdfh")
    assert "not sure" in reply.lower()
