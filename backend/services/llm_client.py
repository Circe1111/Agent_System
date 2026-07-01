"""Unified OpenAI-compatible LLM client.

This module is the single source of truth for talking to the LLM.  Every other
backend module (agents, services, RAG) must import `LLMClient` from here and
must NOT hard-code provider-specific code (no 讯飞星火, no DeepSeek branches).

Environment variables consumed:
    LLM_API_KEY   - bearer token (required for remote calls)
    LLM_BASE_URL  - OpenAI-compatible base URL, e.g. https://opencode.ai/zen/v1
    LLM_MODEL     - chat model id, e.g. opencode-go/deepseek-v4-flash

Transport is `requests` (no `openai` package).
"""
import os
import json
import logging
import requests
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class LLMClient:
    """Thin wrapper over any OpenAI-compatible `/chat/completions` endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        embed_model: Optional[str] = None,
    ) -> None:
        self.api_key: str = api_key or os.getenv("LLM_API_KEY", "")
        self.base_url: str = (
            base_url or os.getenv("LLM_BASE_URL", "https://opencode.ai/zen/v1")
        ).rstrip("/")
        self.model: str = model or os.getenv("LLM_MODEL", "opencode-go/deepseek-v4-flash")
        self.embed_model: str = embed_model or os.getenv("LLM_EMBED_MODEL", "text-embedding-3-small")
        self.timeout: int = int(os.getenv("LLM_TIMEOUT", "60"))

    # ---- internals --------------------------------------------------------

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _chat_url(self) -> str:
        return f"{self.base_url}/chat/completions"

    def _embed_url(self) -> str:
        return f"{self.base_url}/embeddings"

    # ---- public API -------------------------------------------------------

    def chat(
        self,
        messages: List[dict],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ):
        """Call `/chat/completions`.

        Returns the full `requests.Response` object so callers can decide
        whether to read JSON (non-stream) or iterate lines (stream).
        """
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        payload.update(kwargs)
        resp = requests.post(
            self._chat_url(),
            headers=self._headers(),
            json=payload,
            stream=stream,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp

    def chat_text(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> Optional[str]:
        """Convenience helper: returns the assistant text or None on failure."""
        try:
            resp = self.chat(
                messages,
                stream=False,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001
            logger.error("LLMClient.chat_text failed: %s", exc)
            return None

    def embed(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        """Call `/embeddings` and return a list of float vectors."""
        payload = {
            "model": model or self.embed_model,
            "input": texts,
        }
        resp = requests.post(
            self._embed_url(),
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return [item["embedding"] for item in data["data"]]
