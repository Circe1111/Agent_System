import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

DATA_DIR = os.getenv("DATA_DIR", "/app/data")
FAISS_PATH = os.path.join(DATA_DIR, "faiss_index.faiss")


def rebuild():
    print("[FAISS] Checking index...")

    if os.path.exists(FAISS_PATH) and os.path.getsize(FAISS_PATH) > 1000:
        print(f"[FAISS] Index exists at {FAISS_PATH}, skipping rebuild.")
        return 0

    print("[FAISS] Building index from knowledge base...")

    try:
        from rag.document_loader import DocumentLoader
        from rag.embeddings import EmbeddingClient
        from rag.vector_store import VectorStore
    except ImportError as e:
        print(f"[FAISS] Import error: {e}. Skipping index rebuild.")
        return 0

    loader = DocumentLoader(DATA_DIR)
    docs = loader.load_directory()

    if not docs:
        print("[FAISS] No documents found in", DATA_DIR)
        return 0

    print(f"[FAISS] Loaded {len(docs)} documents. Generating embeddings...")

    texts = [doc.content for doc in docs]
    embedder = EmbeddingClient()

    try:
        vectors = embedder.embed(texts)
    except Exception as e:
        print(f"[FAISS] Embedding failed: {e}. Falling back to simple hashing.")
        try:
            embedder = EmbeddingClient(model_type="simple")
            vectors = embedder.embed(texts)
        except Exception as e2:
            print(f"[FAISS] Simple embedding also failed: {e2}")
            return 0

    store = VectorStore(index_path=os.path.join(DATA_DIR, "faiss_index"))
    store.add_documents(docs, vectors)
    store.save()

    print(f"[FAISS] Index built: {len(docs)} docs, {len(vectors)} vectors")
    return 0


if __name__ == "__main__":
    sys.exit(rebuild())
