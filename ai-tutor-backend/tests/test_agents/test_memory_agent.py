# tests/test_agents/test_memory_agent.py
import pytest
from app.agents.memory_agent import MemoryAgent

@pytest.mark.asyncio
async def test_memory_agent_profile_lifecycle(db_session):
    """
    Test MemoryAgent profile creation, update, and performance tracking.
    """
    agent = MemoryAgent()

    # Step 1: Create or get default profile
    profile = await agent.get_profile("testuser")
    assert isinstance(profile, dict)
    assert "topics" in profile
    assert "performance" in profile

    # Step 2: Update age and verify change
    await agent.update_profile("testuser", "age", 15)
    updated = await agent.get_profile("testuser")
    assert updated["age"] == 15

    # Step 3: Update and validate performance
    await agent.update_performance("testuser", "addition", 0.85)
    perf = (await agent.get_profile("testuser"))["performance"]
    assert "addition" in perf
    assert pytest.approx(perf["addition"]["score"], 0.85)
