# tests/test_api/test_quiz.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_quiz_flow(async_client, mock_llm_service):
    """
    Full quiz generation and submission flow test.
    """
    # --- Register and login user ---
    await async_client.post("/api/auth/register", json={
        "username": "quizuser",
        "password": "quizpass123",
        "email": "quiz@example.com"
    })

    token_resp = await async_client.post("/api/auth/token", data={
        "username": "quizuser",
        "password": "quizpass123"
    })

    assert token_resp.status_code == 200
    token_data = token_resp.json()
    assert "access_token" in token_data

    headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    # --- Generate quiz ---
    resp = await async_client.get(
        "/api/quiz/generate",
        params={"topic": "addition", "num_questions": 2},
        headers=headers
    )

    assert resp.status_code == 200
    quiz_data = resp.json()
    assert "questions" in quiz_data
    quiz = quiz_data["questions"]
    assert isinstance(quiz, list)
    assert len(quiz) == 2

    qid = quiz[0]["id"]

    # --- Submit answers ---
    submit_resp = await async_client.post(
        "/api/quiz/submit",
        params={"topic": "addition"},
        json={"answers": {qid: "4"}},
        headers=headers
    )

    assert submit_resp.status_code == 200
    result = submit_resp.json()

    assert "score" in result
    assert isinstance(result["score"], (int, float))
    assert 0.0 <= result["score"] <= 1.0
