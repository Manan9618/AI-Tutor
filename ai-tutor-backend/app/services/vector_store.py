# app/services/vector_store.py
import os
import asyncio
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec


class VectorStoreService:
    """Handles semantic storage and retrieval via Pinecone."""

    def __init__(
        self,
        index_name: str = "ai-tutor-content",
        dimension: int = 384,
        metric: str = "cosine",
    ):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set.")

        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim embeddings

        if index_name not in [i["name"] for i in self.pc.list_indexes()]:
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        self.index = self.pc.Index(index_name)

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Generate sentence embeddings."""
        return self.model.encode(texts, show_progress_bar=False).tolist()

    async def upsert(self, items: List[dict]):
        """
        Upsert items to the vector database.
        Each item: {"id": "exp-1", "text": "Addition is...", "metadata": {...}}
        """
        texts = [item["text"] for item in items]
        vectors = self._embed(texts)
        vectors_to_upsert = [
            (item["id"], vec, item.get("metadata", {}))
            for item, vec in zip(items, vectors)
        ]
        await asyncio.to_thread(self.index.upsert, vectors=vectors_to_upsert)

    async def query(
        self, query_text: str, top_k: int = 3, filter: Optional[dict] = None
    ) -> List[dict]:
        """Query similar vectors."""
        query_vec = self._embed([query_text])[0]
        result = await asyncio.to_thread(
            self.index.query,
            vector=query_vec,
            top_k=top_k,
            filter=filter,
            include_metadata=True,
        )

        matches = []
        for match in result.matches:
            meta = match.metadata or {}
            matches.append(
                {
                    "id": match.id,
                    "score": match.score,
                    "text": meta.get("text", ""),
                    "metadata": {k: v for k, v in meta.items() if k != "text"},
                }
            )
        return matches
