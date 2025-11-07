# tests/test_services/test_vector_store.py
import pytest
from app.services.vector_store import VectorStoreService

@pytest.mark.asyncio
async def test_vector_store_upsert_query(monkeypatch):
    """
    Test upsert and query operations of the vector store with mocked dependencies.
    """

    # --- Mock SentenceTransformer ---
    class MockModel:
        def encode(self, texts, **_):
            return [[0.1, 0.2]] * len(texts)

    monkeypatch.setattr("sentence_transformers.SentenceTransformer", lambda *_, **__: MockModel())

    # --- Mock Pinecone Index ---
    class MockIndex:
        def upsert(self, vectors): 
            self.last_upsert = vectors
        def query(self, vector, top_k, **_):
            return type("Result", (), {"matches": [
                type("Match", (), {"id": "1", "score": 0.99, "metadata": {"text": "mock"}})
            ]})()

    monkeypatch.setattr("pinecone.Index", lambda *_, **__: MockIndex())

    service = VectorStoreService()
    
    # --- Test upsert ---
    await service.upsert([{"id": "1", "text": "test"}])
    
    # --- Test query ---
    results = await service.query("test")

    assert isinstance(results, list)
    assert len(results) == 1
    assert "text" in results[0]
    assert results[0]["text"] == "mock"
