"""Thin LLM agent helpers built on top of LLMClient.

This module is a *facade* over `services.llm_client.LLMClient` for the
streaming / agent code paths.  No provider-specific code lives here.
"""
import json
import logging
from typing import AsyncGenerator, Iterator, List, Optional

import requests

from services.llm_client import LLMClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Async streaming chat (used by stream_service)
# ---------------------------------------------------------------------------

async def chat_stream(
    messages: List[dict],
    temperature: float = 0.7,
    max_tokens: int = 4096,
    **kwargs,
) -> AsyncGenerator[str, None]:
    """Stream chat completions token-by-token.

    Yields decoded content deltas.  Uses `requests` with `stream=True` to
    avoid pulling in the official `openai` package.
    """
    client = LLMClient()
    payload = {
        "model": client.model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }
    payload.update(kwargs)

    try:
        with requests.post(
            client._chat_url(),
            headers=client._headers(),
            json=payload,
            stream=True,
            timeout=client.timeout,
        ) as resp:
            if resp.status_code != 200:
                logger.error("stream HTTP %s: %s", resp.status_code, resp.text)
                return
            for raw in resp.iter_lines(decode_unicode=True):
                if not raw or not raw.startswith("data:"):
                    continue
                data_str = raw[len("data:"):].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
                except Exception:  # noqa: BLE001
                    continue
    except Exception as exc:  # noqa: BLE001
        logger.error("chat_stream failed: %s", exc)
        return


# ---------------------------------------------------------------------------
# Synchronous one-shot chat
# ---------------------------------------------------------------------------

def chat_once(
    messages: List[dict],
    temperature: float = 0.7,
    max_tokens: int = 4096,
    **kwargs,
) -> Optional[str]:
    """Single-turn chat helper.  Returns the assistant text or None."""
    return LLMClient().chat_text(
        messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
