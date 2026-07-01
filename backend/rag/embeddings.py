import os
import numpy as np
from dotenv import load_dotenv
from typing import List

load_dotenv()


class EmbeddingClient:
    def __init__(self, model_type: str = "local"):
        self.model_type = model_type
        self.model = None
        self._load_model()

    def _load_model(self):
        if self.model_type == "local":
            try:
                import os
                os.environ["TRANSFORMERS_OFFLINE"] = "0"
                from text2vec import SentenceModel
                self.model = SentenceModel("shibing624/text2vec-base-chinese", device="cpu")
            except Exception as e:
                print(f">>> text2vec初始化失败: {e}，将使用简单向量表示")
                self.model_type = "simple"
        elif self.model_type == "xunfei":
            self._init_xunfei()

    def _init_xunfei(self):
        self.spark_app_id = os.getenv("SPARK_APP_ID")
        self.spark_api_key = os.getenv("SPARK_API_KEY")
        self.spark_api_secret = os.getenv("SPARK_API_SECRET")

    def embed(self, texts: List[str]) -> List[np.ndarray]:
        if self.model_type == "local" and self.model:
            return self._embed_local(texts)
        elif self.model_type == "xunfei":
            return self._embed_xunfei(texts)
        elif self.model_type == "simple":
            return self._embed_simple(texts)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        try:
            text = text.encode('utf-8', errors='replace').decode('utf-8')
        except:
            text = ''.join(c for c in text if c.isprintable() or c in '\n\r\t ')
        return text

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
            embeddings = self.model.encode(texts, show_progress_bar=False)
            return [np.array(embedding) for embedding in embeddings]
        except Exception as e:
            print(f">>> 本地Embedding失败: {e}")
            return [np.zeros(768) for _ in texts]

    def _embed_xunfei(self, texts: List[str]) -> List[np.ndarray]:
        try:
            import requests
            import base64

            auth_string = f"{self.spark_api_key}:{self.spark_api_secret}"
            encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {encoded_auth}"
            }

            results = []
            for text in texts:
                payload = {
                    "model": "spark-embedding-3",
                    "input": text,
                    "parameters": {"text_type": "query"}
                }

                response = requests.post(
                    "https://spark-api-open.xf-yun.com/v1/text/embeddings",
                    json=payload, headers=headers, timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    embedding = result["data"][0]["embedding"]
                    results.append(np.array(embedding))
                else:
                    print(f">>> 讯飞Embedding API错误: {response.text}")
                    results.append(np.zeros(1024))

            return results
        except Exception as e:
            print(f">>> 讯飞Embedding请求异常: {e}")
            return [np.zeros(1024) for _ in texts]

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed([query])[0]