"""
ollama_client.py — Async wrapper around Ollama's embedding API.

Why a separate module?
  Keeping HTTP concerns isolated means the rest of the codebase never
  has to know *how* we get embeddings — only that we call get_embedding()
  and receive a list of floats back.  If we ever swap Ollama for OpenAI
  or a local sentence-transformer, only this file changes.

How Ollama embeddings work:
  Ollama exposes a REST endpoint:
    POST http://localhost:11434/api/embeddings
    Body: { "model": "<model-name>", "prompt": "<text>" }
    Response: { "embedding": [0.123, -0.456, ...] }   ← 768 floats for nomic-embed-text

  We send the text we want embedded, and get back a vector that encodes
  the *semantic meaning* of that text in 768-dimensional space.
  Texts that mean similar things will have vectors that are close together
  (measured by cosine similarity).
"""

import httpx
from typing import Any


class OllamaClient:
    """
    Async HTTP client for the Ollama embeddings endpoint.

    Usage:
        async with OllamaClient() as client:
            vector = await client.get_embedding("What is machine learning?")
            # vector is a list of 768 floats
    """

    def __init__(self, base_url: str, model: str):
        """
        Args:
            base_url: Root URL of the Ollama server, e.g. "http://localhost:11434"
            model:    The embedding model to use, e.g. "nomic-embed-text"
        """
        self.base_url = base_url.rstrip("/")
        self.model = model

        # httpx.AsyncClient is reusable across many requests — we create it
        # once and reuse it so we don't open a new TCP connection every call.
        # timeout=30 seconds gives Ollama enough time on first use when it has
        # to load the model weights into memory.
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_embedding(self, text: str) -> list[float]:
        """
        Send `text` to Ollama and return its embedding vector.

        Args:
            text: Any string — a document chunk, a user query, anything.

        Returns:
            A list of 768 floats (for nomic-embed-text).

        Raises:
            httpx.HTTPStatusError: if Ollama returns a non-2xx response.
            httpx.ConnectError:    if Ollama isn't running.
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": text,  # Ollama uses "prompt" (not "input") for embeddings
        }

        response = await self._client.post(
            f"{self.base_url}/api/embeddings",
            json=payload,
        )
        # Raise an exception for 4xx / 5xx so callers get a clear error.
        response.raise_for_status()

        data = response.json()
        # The response shape is: {"embedding": [float, float, ...]}
        return data["embedding"]

    async def health_check(self) -> bool:
        """
        Ping Ollama to confirm it's reachable before we try to index anything.

        Returns True if reachable, False otherwise (never raises).
        """
        try:
            r = await self._client.get(f"{self.base_url}/api/tags")
            return r.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        """Release the underlying HTTP connection pool."""
        await self._client.aclose()

    # ------------------------------------------------------------------ #
    # Context manager support — lets callers use `async with OllamaClient`  #
    # ------------------------------------------------------------------ #
    async def __aenter__(self) -> "OllamaClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
