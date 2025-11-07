# tests/conftest.py
import asyncio
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.services.llm_service import LLMService
from app.services.vector_store import VectorStoreService

# ============================================================
# ✅ TEST DATABASE SETUP
# ============================================================
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Async engine and session for testing
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ============================================================
# ✅ EVENT LOOP FIXTURE (for pytest-asyncio)
# ============================================================
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================
# ✅ DATABASE SESSION FIXTURE
# ============================================================
@pytest.fixture(scope="function")
async def db_session():
    """Provide a clean in-memory DB for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ============================================================
# ✅ FASTAPI TEST CLIENT FIXTURES
# ============================================================
@pytest.fixture
def client(db_session):
    """Synchronous test client (used for non-async API tests)."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(db_session):
    """Asynchronous test client for async API endpoints."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ============================================================
# ✅ MOCK LLM SERVICE
# ============================================================
class MockLLMService(LLMService):
    """Mock implementation of LLMService for tests."""

    async def generate(self, *args, **kwargs):
        return type("Response", (), {"content": "Mocked LLM response"})()

    async def generate_quiz(self, *args, **kwargs):
        return [
            {
                "id": 1,
                "question": "What is 2+2?",
                "choices": ["3", "4", "5", "6"],
                "answer": 1,
                "explanation": "2+2=4",
            }
        ]


@pytest.fixture
def mock_llm_service(monkeypatch):
    """Patch the LLMService globally with mock behavior."""
    mock = MockLLMService()
    # Replace BaseAgent.call_llm and LLMService initialization
    monkeypatch.setattr("app.agents.base_agent.BaseAgent.call_llm", lambda *_, **__: "mocked llm response")
    monkeypatch.setattr("app.services.llm_service.LLMService", lambda: mock)
    return mock


# ============================================================
# ✅ MOCK VECTOR STORE SERVICE
# ============================================================
class MockVectorStore(VectorStoreService):
    """Mock vector store to simulate Pinecone/SentenceTransformer."""

    def __init__(self):
        self.memory = {}

    async def upsert(self, items):
        for item in items:
            self.memory[item["id"]] = item

    async def query(self, query_text, top_k: int = 3, filter=None):
        return [
            {
                "id": "mock-1",
                "score": 0.98,
                "text": f"Mocked vector context for '{query_text}'",
                "metadata": {"topic": "addition", "level": "beginner"},
            }
        ]


@pytest.fixture
def mock_vector_store(monkeypatch):
    """Patch VectorStoreService globally with mock version."""
    mock = MockVectorStore()
    monkeypatch.setattr("app.services.vector_store.VectorStoreService", lambda: mock)
    return mock
