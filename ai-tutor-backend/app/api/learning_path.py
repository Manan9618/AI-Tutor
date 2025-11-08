# app/api/learning_path.py
import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.api.auth import get_current_user
from app.agents.path_generator import PathGeneratorAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.analytics_agent import AnalyticsAgent

router = APIRouter(tags=["Learning Path"])
logger = logging.getLogger(__name__)

# Initialize agents only once
path_generator = PathGeneratorAgent()
memory_agent = MemoryAgent()
analytics_agent = AnalyticsAgent()


# Helper to handle both sync and async functions
async def maybe_await(func, *args, **kwargs):
    """Call a function that could be sync or async safely."""
    try:
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result
    except Exception as e:
        raise e


@router.get("/", tags=["Learning Path"])
async def learning_path_root():
    """Root endpoint for Learning Path"""
    return {"message": "🧭 Learning Path API active. Use /next-topic or /roadmap for details."}


@router.get("/next-topic", response_model=Dict[str, Any], tags=["Learning Path"])
async def get_next_topic(current_user: str = Depends(get_current_user)):
    """Suggest the next topic for the learner"""
    try:
        next_topic = await maybe_await(path_generator.generate_next_topic, current_user, memory_agent)
        return {"next_topic": next_topic}
    except Exception as e:
        logger.exception("❌ Error generating next topic")
        raise HTTPException(status_code=500, detail=f"Error generating next topic: {str(e)}")


@router.get("/roadmap", tags=["Learning Path"])
async def get_roadmap(current_user: str = Depends(get_current_user)):
    """
    ✅ Return a persistent learning path for the current user.
    If not found, generate a new one and store it in memory.
    """
    try:
        # 1️⃣ Try to load existing path
        saved_path = await maybe_await(memory_agent.get_user_learning_path, current_user)
        if saved_path:
            return {"topics": saved_path}

        # 2️⃣ Generate a new roadmap using the path generator
        roadmap = await maybe_await(path_generator.generate_roadmap, current_user, memory_agent)

        # Fallback in case LLM response fails or is empty
        if not roadmap or not isinstance(roadmap, list):
            roadmap = ["Introduction to AI", "Neural Networks", "Machine Learning Basics"]

        topics = [{"id": i + 1, "name": t, "completed": False} for i, t in enumerate(roadmap)]

        # 3️⃣ Save for persistence
        await maybe_await(memory_agent.save_learning_path, current_user, topics)

        return {"topics": topics}

    except Exception as e:
        logger.exception("❌ Error generating roadmap")
        raise HTTPException(status_code=500, detail=f"Error generating roadmap: {str(e)}")


@router.post("/update", tags=["Learning Path"])
async def update_learning_path(payload: Dict[str, Any], current_user: str = Depends(get_current_user)):
    """
    ✅ Update the user's learning path and record progress.
    Expected payload: { "topics": [ {id, name, completed, ...}, ... ] }
    """
    try:
        topics = payload.get("topics", [])
        if not isinstance(topics, list):
            raise HTTPException(status_code=400, detail="Invalid topics format")

        # Save updated path in memory
        await maybe_await(memory_agent.save_learning_path, current_user, topics)

        # Compute progress stats
        completed = sum(1 for t in topics if t.get("completed"))
        total = len(topics)
        progress = round((completed / total) * 100, 2) if total > 0 else 0

        # Record learning progress (safe even if not async)
        if hasattr(analytics_agent, "generate_dashboard_metrics"):
            await maybe_await(analytics_agent.generate_dashboard_metrics, current_user, memory_agent)

        return {"message": "✅ Learning path updated successfully", "progress": progress}

    except Exception as e:
        logger.exception("❌ Error updating learning path")
        raise HTTPException(status_code=500, detail=f"Error updating learning path: {str(e)}")
