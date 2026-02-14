import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import settings


class ChromaStore:
    client: chromadb.PersistentClient | None = None
    collection: Collection | None = None


chroma_store = ChromaStore()


def init_chroma() -> None:
    chroma_store.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    chroma_store.collection = chroma_store.client.get_or_create_collection(
        name="cv_chunks", metadata={"hnsw:space": "cosine"}
    )


def get_collection() -> Collection:
    if not chroma_store.collection:
        raise RuntimeError("Chroma not initialized")
    return chroma_store.collection
