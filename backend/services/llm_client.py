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
import hmac
import hashlib
import base64
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse
from typing import Any, List, Optional

from dotenv import load_dotenv

_ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(_ENV_FILE)

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
            base_url
            or os.getenv("LLM_BASE_URL")
            or os.getenv("SPARK_BASE_URL")
            or os.getenv("LLM_BASE_URL", "https://opencode.ai/zen/v1")
        ).rstrip("/")
        self.model: str = model or os.getenv("LLM_MODEL", "opencode-go/deepseek-v4-flash")
        self.embed_model: str = embed_model or os.getenv("LLM_EMBED_MODEL", "text-embedding-3-small")
        self.timeout: int = int(os.getenv("LLM_TIMEOUT", "60"))
        self.app_id: str = os.getenv("SPARK_APP_ID") or os.getenv("LLM_APP_ID", "")

    # ---- internals --------------------------------------------------------

    def _headers(self) -> dict:
        if "xf-yun.com" in self.base_url:
            api_key = os.getenv("SPARK_API_KEY") or os.getenv("LLM_API_KEY")
            api_secret = os.getenv("SPARK_API_SECRET") or os.getenv("LLM_API_SECRET")
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            if self.app_id:
                headers["X-Appid"] = self.app_id
            if api_key and api_secret:
                encoded_auth = base64.b64encode(
                    f"{api_key}:{api_secret}".encode('utf-8')
                ).decode('utf-8')
                headers["Authorization"] = f"Bearer {encoded_auth}"
            return headers
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _spark_signed_url(self) -> str:
        """Construct a signed URL for Xunfei Spark (HMAC-SHA256) when required.

        Uses SPARK_APP_ID / SPARK_API_KEY / SPARK_API_SECRET if available,
        otherwise falls back to LLM_API_KEY and no signature.
        """
        # prefer explicit SPARK_* env vars
        app_id = os.getenv("SPARK_APP_ID")
        api_key = os.getenv("SPARK_API_KEY") or os.getenv("LLM_API_KEY")
        api_secret = os.getenv("SPARK_API_SECRET") or os.getenv("LLM_API_SECRET")

        # base_url may already include the full path (e.g. /x2/chat/completions)
        base = self.base_url
        parsed = urlparse(base)
        path = parsed.path or "/x2/chat/completions"

        # date in GMT
        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

        if not api_secret:
            logger.debug("No Spark secret found; falling back to unsigned URL")
            query = urlencode({
                "date": date,
                "host": "spark-api-open.xf-yun.com",
            })
            return f"{base}?{query}"

        signature_origin = f"host: spark-api-open.xf-yun.com\ndate: {date}\nPOST {path} HTTP/1.1"
        signature = hmac.new(
            api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256,
        ).digest()
        signature_base64 = base64.b64encode(signature).decode()

        authorization_origin = (
            f'api_key="{api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature_base64}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
        query = urlencode({
            "authorization": authorization,
            "date": date,
            "host": "spark-api-open.xf-yun.com",
        })

        try:
            masked_key = (api_key[:4] + '...' + api_key[-4:]) if api_key and len(api_key) > 8 else '***'
        except Exception:
            masked_key = '***'
        logger.debug("Built Spark signed URL (api_key=%s, path=%s, date=%s)", masked_key, path, date)
        return f"{base}?{query}"

    def _chat_url(self) -> str:
        url = self.base_url.rstrip('/')
        if url.endswith('/chat/completions') or url.endswith('/v2/chat') or url.endswith('/chat'):
            return url
        return f"{url}/chat/completions"

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

        is_spark = "xf-yun.com" in self.base_url

        resp = requests.post(
            self._spark_signed_url() if is_spark else self._chat_url(),
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