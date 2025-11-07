# tests/test_agents/test_explanation_agent.py
import pytest
from app.agents.explanation_agent import ExplanationAgent

@pytest.mark.asyncio
async def test_explanation_agent(mock_llm_service):
    """
    Test ExplanationAgent end-to-end explanation generation.
    Ensures that explanations use base content or mock LLM output.
    """
    # Inject a small mock content repository
    agent = ExplanationAgent(content_repo={"addition": "Base: 1+1=2"})

    # Call explanation method (async safe)
    result = await agent.explain_concept(
        topic="addition",
        level="beginner",
        style="visual",
        base_content="Base: 1+1=2"
    )

    assert isinstance(result, str)
    assert any(word in result.lower() for word in ["mock", "1+1", "addition"])
