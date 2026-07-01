import os
import numpy as np
from dotenv import load_dotenv
from typing import List

load_dotenv()


class EmbeddingClient:
    """Embedding client with three modes:

    * ``openai``  — primary; uses the unified ``LLMClient`` (OpenAI-compatible)
                    hitting ``/embeddings``.  Configure via LLM_API_KEY /
                    LLM_BASE_URL / LLM_EMBED_MODEL.
    * ``local``   — offline fallback; uses ``text2vec`` SentenceModel
                    (``shibing624/text2vec-base-chinese``).  Falls back to the
                    ``simple`` mode if the model is unavailable.
    * ``simple``  — last-resort deterministic hash vectors (no network, no
                    model download).  Used only when nothing else works.
    """

    def __init__(self, model_type: str = "openai"):
        self.model_type = model_type
        self.model = None
        self._client = None
        self._load_model()

    def _load_model(self):
        if self.model_type == "openai":
            try:
                from services.llm_client import LLMClient
                self._client = LLMClient()
            except Exception as exc:  # noqa: BLE001
                print(f">>> OpenAI Embedding 初始化失败: {exc}，回退到 local")
                self.model_type = "local"
                self._load_model()
        if self.model_type == "local":
            try:
                os.environ["TRANSFORMERS_OFFLINE"] = "0"
                from text2vec import SentenceModel
                self.model = SentenceModel("shibing624/text2vec-base-chinese", device="cpu")
            except Exception as e:
                print(f">>> text2vec初始化失败: {e}，将使用简单向量表示")
                self.model_type = "simple"
        elif self.model_type == "simple":
            return

    # ---- public ------------------------------------------------------------

    def embed(self, texts: List[str]) -> List[np.ndarray]:
        if self.model_type == "openai" and self._client is not None:
            return self._embed_openai(texts)
        if self.model_type == "local" and self.model is not None:
            return self._embed_local(texts)
        if self.model_type == "simple":
            return self._embed_simple(texts)
        raise ValueError(f"不支持或未初始化的模型类型: {self.model_type}")

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed([query])[0]

    # ---- internals ---------------------------------------------------------

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        try:
            text = text.encode('utf-8', errors='replace').decode('utf-8')
        except Exception:
            text = ''.join(c for c in text if c.isprintable() or c in '\n\r\t ')
        return text

    def _embed_openai(self, texts: List[str]) -> List[np.ndarray]:
        try:
            cleaned = [self._clean_text(t) for t in texts]
            vecs = self._client.embed(cleaned)
            return [np.asarray(v, dtype=np.float32) for v in vecs]
        except Exception as exc:  # noqa: BLE001
            print(f">>> OpenAI Embedding 请求失败: {exc}，回退到 simple")
            return self._embed_simple(texts)

    def _embed_simple(self, texts: List[str]) -> List[np.ndarray]:
        import hashlib
        results = []
        for text in texts:
            text = self._clean_text(text)
            h = hashlib.md5(text.encode('utf-8'))
            hash_bytes = h.digest()
            embedding = np.array([int(hash_bytes[i]) / 255.0 for i in range(16)], dtype=np.float32)
            results.append(embedding)
        return results

    def _embed_local(self, texts: List[str]) -> List[np.ndarray]:
        try:
            cleaned = [self._clean_text(t) for t in texts]
            embeddings = self.model.encode(cleaned, show_progress_bar=False)
            return [np.array(embedding) for embedding in embeddings]
        except Exception as e:
            print(f">>> 本地Embedding失败: {e}")
            return [np.zeros(768) for _ in texts]
