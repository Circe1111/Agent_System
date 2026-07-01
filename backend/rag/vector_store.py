import os
import pickle
import numpy as np
from typing import List, Tuple, Optional
from .document_loader import Document


class VectorStore:
    def __init__(self, index_path: str = "data/faiss_index", embedding_dim: int = 768):
        self.index_path = index_path
        self.embedding_dim = embedding_dim
        self.index = None
        self.documents = []
        self._init_faiss()

    def _init_faiss(self):
        try:
            import faiss
            self.index = faiss.IndexFlatL2(self.embedding_dim)
        except ImportError:
            raise ImportError("请安装 faiss-cpu: pip install faiss-cpu")

    def add_documents(self, docs: List[Document], embeddings: List[np.ndarray]):
        if len(docs) != len(embeddings):
            raise ValueError("文档数量与embedding数量不匹配")

        if embeddings:
            self.embedding_dim = embeddings[0].shape[0]
            self.index = None
            self._init_faiss()

            embeddings_array = np.array(embeddings).astype(np.float32)
            self.index.add(embeddings_array)

        self.documents.extend(docs)

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Tuple[Document, float]]:
        if self.index.ntotal == 0:
            return []

        query_array = np.array([query_embedding]).astype(np.float32)
        distances, indices = self.index.search(query_array, top_k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append((self.documents[idx], float(distances[0][i])))

        return results

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        import faiss
        faiss.write_index(self.index, f"{self.index_path}.faiss")

        with open(f"{self.index_path}_docs.pkl", "wb") as f:
            pickle.dump(self.documents, f)

    def load(self) -> bool:
        faiss_path = f"{self.index_path}.faiss"
        docs_path = f"{self.index_path}_docs.pkl"

        if not os.path.exists(faiss_path) or not os.path.exists(docs_path):
            return False

        try:
            import faiss
            self.index = faiss.read_index(faiss_path)

            with open(docs_path, "rb") as f:
                self.documents = pickle.load(f)

            return True
        except Exception as e:
            print(f">>> 加载索引失败: {e}")
            return False

    def get_document_count(self) -> int:
        return len(self.documents)

    def is_empty(self) -> bool:
        return self.index.ntotal == 0


class RAGRetriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def retrieve(self, query: str, embedding, top_k: int = 3) -> List[dict]:
        if self.vector_store.is_empty():
            return []

        query_embedding = embedding.embed_query(query)
        results = self.vector_store.search(query_embedding, top_k)

        retrieved_texts = []
        for doc, distance in results:
            retrieved_texts.append({
                "content": doc.content,
                "source": doc.metadata.get("relative_path", doc.metadata.get("file_name", "未知")),
                "score": 1.0 / (1.0 + distance)
            })

        return retrieved_texts

    def retrieve_with_scores(self, query: str, embedding, top_k: int = 3) -> List[Tuple[str, float]]:
        if self.vector_store.is_empty():
            return []

        query_embedding = embedding.embed_query(query)
        results = self.vector_store.search(query_embedding, top_k)

        return [(doc.content, score) for doc, score in results]