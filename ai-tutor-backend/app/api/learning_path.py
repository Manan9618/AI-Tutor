# import asyncio
# import logging
# import re
# from fastapi import APIRouter, Depends, HTTPException
# from typing import Dict, Any
# from app.api.auth import get_current_user
# from app.agents.path_generator import PathGeneratorAgent
# from app.agents.memory_agent import MemoryAgent
# from app.agents.analytics_agent import AnalyticsAgent

# router = APIRouter(tags=["Learning Path"])
# logger = logging.getLogger(__name__)

# # Initialize agents only once
# path_generator = PathGeneratorAgent()
# memory_agent = MemoryAgent()
# analytics_agent = AnalyticsAgent()


# # Helper to handle both sync and async functions
# async def maybe_await(func, *args, **kwargs):
#     """Call a function that could be sync or async safely."""
#     try:
#         result = func(*args, **kwargs)
#         if asyncio.iscoroutine(result):
#             return await result
#         return result
#     except Exception as e:
#         raise e


# @router.get("/", tags=["Learning Path"])
# async def learning_path_root():
#     """Root endpoint for Learning Path"""
#     return {"message": "🧭 Learning Path API active. Use /next-topic or /roadmap for details."}


# @router.get("/next-topic", response_model=Dict[str, Any], tags=["Learning Path"])
# async def get_next_topic(current_user: str = Depends(get_current_user)):
#     """Suggest the next topic for the learner"""
#     try:
#         next_topic = await maybe_await(path_generator.generate_next_topic, current_user, memory_agent)
#         return {"next_topic": next_topic}
#     except Exception as e:
#         logger.exception("❌ Error generating next topic")
#         raise HTTPException(status_code=500, detail=f"Error generating next topic: {str(e)}")


# @router.get("/roadmap", tags=["Learning Path"])
# async def get_roadmap(current_user: str = Depends(get_current_user)):
#     """
#     ✅ Return a persistent learning path for the current user.
#     If not found, generate a new one and store it in memory.
#     """
#     try:
#         # 1️⃣ Try to load existing path
#         saved_path = await maybe_await(memory_agent.get_user_learning_path, current_user)
#         if saved_path:
#             return {"topics": saved_path}

#         # 2️⃣ Generate a new roadmap using the path generator
#         roadmap = await maybe_await(path_generator.generate_roadmap, current_user, memory_agent)

#         # Fallback in case LLM response fails or is empty
#         if not roadmap or not isinstance(roadmap, list):
#             roadmap = ["Introduction to AI", "Neural Networks", "Machine Learning Basics"]

#         # 🧹 Clean topic names
#         def clean_topic_name(t: str) -> str:
#             """
#                 Remove leading numbers, markdown headers, bullets, and extra whitespace.
#                  Handles patterns like:
#                 - "1. Topic"
#                 - "2) Topic"
#                 - "- Topic"
#                 - "### Topic"
#                 - "**Topic**"
#             """
#             # Remove leading numbering/headers/bullets
#             t = re.sub(r'^\s*(?:\d+[\.\)]\s*|[-*]\s*|#{1,6}\s*)', '', t)
    
#             # Remove trailing markdown bold/italic (e.g., **text**, *text*)
#             t = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', t)
    
#             # Remove extra whitespace
#             t = t.strip()
    
#             #If empty after cleaning, use a fallback
#             if not t:
#                 t = "Untitled Topic"
        
#             return t

#         # Inside /roadmap endpoint
#         cleaned_topics = [clean_topic_name(t) for t in roadmap]
#         topics = [{"name": t, "completed": False} for t in cleaned_topics]

#         # 3️⃣ Save for persistence
#         await maybe_await(memory_agent.save_learning_path, current_user, topics)

#         return {"topics": topics}

#     except Exception as e:
#         logger.exception("❌ Error generating roadmap")
#         raise HTTPException(status_code=500, detail=f"Error generating roadmap: {str(e)}")


# @router.post("/update", tags=["Learning Path"])
# async def update_learning_path(payload: Dict[str, Any], current_user: str = Depends(get_current_user)):
#     """
#     ✅ Update the user's learning path and record progress.
#     Expected payload: { "topics": [ {id, name, completed, ...}, ... ] }
#     """
#     try:
#         topics = payload.get("topics", [])
#         if not isinstance(topics, list):
#             raise HTTPException(status_code=400, detail="Invalid topics format")

#         # Save updated path in memory
#         await maybe_await(memory_agent.save_learning_path, current_user, topics)

#         # Compute progress stats
#         completed = sum(1 for t in topics if t.get("completed"))
#         total = len(topics)
#         progress = round((completed / total) * 100, 2) if total > 0 else 0

#         # Record learning progress (safe even if not async)
#         if hasattr(analytics_agent, "generate_dashboard_metrics"):
#             await maybe_await(analytics_agent.generate_dashboard_metrics, current_user, memory_agent)

#         return {"message": "✅ Learning path updated successfully", "progress": progress}

#     except Exception as e:
#         logger.exception("❌ Error updating learning path")
#         raise HTTPException(status_code=500, detail=f"Error updating learning path: {str(e)}")


import asyncio
import logging
import re
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
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


def clean_topic_name(t: str) -> str:
    """
    Remove markdown, numbering, bullets, and extra whitespace.
    """
    if not isinstance(t, str):
        t = str(t)
    t = re.sub(r'^\s*(?:\d+[\.\)]\s*|[-*]\s*|#{1,6}\s*)', '', t)
    t = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', t)
    t = t.strip()
    return t or "Untitled Topic"


@router.get("/roadmap", tags=["Learning Path"])
async def get_roadmap(current_user: str = Depends(get_current_user)):
    """
    ✅ Return a persistent learning path for the current user.
    Response includes:
      - topics: full list with {name, completed}
      - completed_topics: list of completed topic names (for Home.jsx)
    """
    try:
        # 1️⃣ Try to load existing path
        saved_path = await maybe_await(memory_agent.get_user_learning_path, current_user)
        if saved_path:
            # Ensure all topics have 'name' and 'completed'
            normalized = []
            for t in saved_path:
                if isinstance(t, str):
                    normalized.append({"name": clean_topic_name(t), "completed": False})
                else:
                    name = clean_topic_name(t.get("name") or t.get("topic") or str(t))
                    completed = bool(t.get("completed", False))
                    normalized.append({"name": name, "completed": completed})
            
            # ✅ Extract completed topic names
            completed_topics = [t["name"] for t in normalized if t["completed"]]
            return {
                "topics": normalized,
                "completed_topics": completed_topics  # 👈 REQUIRED by Home.jsx
            }

        # 2️⃣ Generate new roadmap
        roadmap = await maybe_await(path_generator.generate_roadmap, current_user, memory_agent)
        if not roadmap or not isinstance(roadmap, list):
            roadmap = ["Introduction to AI", "Neural Networks", "Machine Learning Basics"]

        cleaned_names = [clean_topic_name(t) for t in roadmap]
        topics = [{"name": name, "completed": False} for name in cleaned_names]
        completed_topics = []  # none completed yet

        # 3️⃣ Save and return
        await maybe_await(memory_agent.save_learning_path, current_user, topics)
        return {
            "topics": topics,
            "completed_topics": completed_topics  # 👈 always include
        }

    except Exception as e:
        logger.exception("❌ Error generating roadmap")
        raise HTTPException(status_code=500, detail=f"Error generating roadmap: {str(e)}")


@router.post("/update", tags=["Learning Path"])
async def update_learning_path(payload: Dict[str, Any], current_user: str = Depends(get_current_user)):
    """
    ✅ Update the user's learning path and record progress.
    Expected payload: { "topics": [ { "name": "...", "completed": true }, ... ] }
    """
    try:
        topics = payload.get("topics", [])
        if not isinstance(topics, list):
            raise HTTPException(status_code=400, detail="Invalid topics format")

        # Normalize incoming topics (ensure 'name' exists)
        normalized = []
        for t in topics:
            if isinstance(t, str):
                normalized.append({"name": clean_topic_name(t), "completed": False})
            else:
                name = clean_topic_name(t.get("name") or t.get("topic") or str(t))
                completed = bool(t.get("completed", False))
                normalized.append({"name": name, "completed": completed})

        # Save updated path
        await maybe_await(memory_agent.save_learning_path, current_user, normalized)

        # Compute progress
        completed = sum(1 for t in normalized if t["completed"])
        total = len(normalized)
        progress = round((completed / total) * 100, 2) if total > 0 else 0

        # Trigger analytics update
        if hasattr(analytics_agent, "generate_dashboard_metrics"):
            await maybe_await(analytics_agent.generate_dashboard_metrics, current_user, memory_agent)

        return {
            "message": "✅ Learning path updated successfully",
            "progress": progress,
            "completed_topics": [t["name"] for t in normalized if t["completed"]]  # optional
        }

    except Exception as e:
        logger.exception("❌ Error updating learning path")
        raise HTTPException(status_code=500, detail=f"Error updating learning path: {str(e)}")