"""Optional Anthropic-backed provider.

Only imported/instantiated when `AI_PROVIDER=anthropic` and `AI_API_KEY`
is set, so the `anthropic` package is not a hard dependency for
environments that just want the free mock provider.
"""
from __future__ import annotations


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        try:
            import anthropic  # type: ignore
        except ImportError as exc:  # pragma: no cover - exercised only when selected
            raise RuntimeError(
                "The 'anthropic' package is required for AI_PROVIDER=anthropic. "
                "Install it with `pip install anthropic`."
            ) from exc

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def generate(self, prompt: str, *, context: str | None = None) -> str:  # pragma: no cover
        system = "You are a helpful, concise library assistant. Recommend books from the given catalog context when possible."
        full_prompt = prompt if not context else f"Catalog context:\n{context}\n\nQuestion: {prompt}"
        response = self._client.messages.create(
            model=self._model,
            max_tokens=300,
            system=system,
            messages=[{"role": "user", "content": full_prompt}],
        )
        return "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
