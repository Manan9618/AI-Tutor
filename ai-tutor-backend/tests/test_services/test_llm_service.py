# tests/test_services/test_llm_service.py
import pytest
from unittest.mock import AsyncMock
from app.services.llm_service import LLMService, LLMResponse


@pytest.mark.asyncio
async def test_llm_service_generate(monkeypatch):
    """
    Test basic text generation using mocked AsyncOpenAI client.
    """

    # --- Mock OpenAI response ---
    mock_choice = AsyncMock()
    mock_choice.message.content = "mocked response"

    mock_completion = AsyncMock()
    mock_completion.choices = [mock_choice]
    mock_completion.usage = None

    # --- Mock client ---
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

    # Patch inside LLMService
    monkeypatch.setattr("app.services.llm_service.AsyncOpenAI", lambda **_: mock_client)

    # --- Initialize and test ---
    service = LLMService(api_key="fake-key")

    result = await service.generate(prompt="Hello", system_prompt="Hi")

    assert isinstance(result, LLMResponse)
    assert result.content == "mocked response"
    assert result.usage is None

    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs["messages"][0]["role"] == "system"
    assert call_args.kwargs["messages"][1]["content"] == "Hello"


@pytest.mark.asyncio
async def test_llm_service_generate_quiz(monkeypatch):
    """
    Test quiz generation using mocked JSON response from LLM.
    """

    # --- Mock LLM JSON output ---
    mock_message = AsyncMock()
    mock_message.content = '''
    [
        {
            "id": 1,
            "question": "What is 2 + 2?",
            "choices": ["3", "4", "5", "6"],
            "answer": 1,
            "explanation": "Basic addition"
        }
    ]
    '''.strip()

    mock_completion = AsyncMock()
    mock_completion.choices = [AsyncMock(message=mock_message)]

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

    monkeypatch.setattr("app.services.llm_service.AsyncOpenAI", lambda **_: mock_client)

    service = LLMService()
    quiz = await service.generate_quiz(topic="addition", level="beginner", num=1)

    assert isinstance(quiz, list)
    assert len(quiz) == 1
    assert quiz[0]["question"] == "What is 2 + 2?"
    assert quiz[0]["choices"][1] == "4"
    assert quiz[0]["answer"] == 1
