# tests/test_services/test_content_retrieval.py
import pytest
from app.services.content_retrieval import ContentRetrievalService

@pytest.mark.asyncio
async def test_rag_explain(monkeypatch):
    """
    Test the RAG-based explanation generation with mocked vector and LLM services.
    """

    # --- Mock Vector Store Service ---
    class MockVectorStore:
        async def query(self, query_text, top_k=3):
            return [{"text": "1+1=2 mock context"}]

    # --- Mock LLM Service ---
    class MockLLMService:
        async def generate(self, prompt, system_prompt=None):
            class MockResponse:
                content = "Mocked explanation for addition: 1+1=2"
            return MockResponse()

    monkeypatch.setattr("app.services.content_retrieval.VectorStoreService", lambda: MockVectorStore())
    monkeypatch.setattr("app.services.content_retrieval.LLMService", lambda: MockLLMService())

    service = ContentRetrievalService()
    result = await service.rag_explain(
        topic="addition",
        user_query="What is 1+1?",
        level="beginner"
    )

    assert isinstance(result, str)
    assert "1+1=2" in result or "mock" in result.lower()
