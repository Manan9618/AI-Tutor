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
    ✅ Return hierarchical learning path:
    [
      { "name": "Core", "topics": [ {"name": "...", "completed": false}, ... ] },
      { "name": "GenAI", "topics": [...] }
    ]
    
    Also returns flat "completed_topics" for Home.jsx compatibility.
    """
    try:
        # 1️⃣ Try to load existing hierarchical path
        saved_roadmap = await maybe_await(memory_agent.get_user_learning_path, current_user)
        
        if saved_roadmap and isinstance(saved_roadmap, list) and saved_roadmap:
            # Check if it's already hierarchical (new format)
            if isinstance(saved_roadmap[0], dict) and "topics" in saved_roadmap[0]:
                # It's hierarchical → use as-is
                roadmap = saved_roadmap
            else:
                # It's flat (old format) → migrate to hierarchical
                # Put all topics under "Core Curriculum"
                flat_topics = []
                for t in saved_roadmap:
                    if isinstance(t, str):
                        flat_topics.append({"name": clean_topic_name(t), "completed": False})
                    else:
                        name = clean_topic_name(t.get("name") or t.get("topic") or str(t))
                        completed = bool(t.get("completed", False))
                        flat_topics.append({"name": name, "completed": completed})
                
                roadmap = [{
                    "name": "📚 Core Curriculum",
                    "topics": flat_topics
                }]
        else:
            # 2️⃣ Generate new hierarchical roadmap
            generated = await maybe_await(path_generator.generate_roadmap, current_user, memory_agent)
            
            if not generated or not isinstance(generated, list):
                # Fallback to flat → wrap in core
                fallback_topics = ["Introduction to AI", "Neural Networks", "Machine Learning Basics"]
                roadmap = [{
                    "name": "📚 Core Curriculum",
                    "topics": [{"name": clean_topic_name(t), "completed": False} for t in fallback_topics]
                }]
            else:
                # Ensure each section has proper topic objects
                roadmap = []
                for section in generated:
                    if isinstance(section, str):
                        # Very rare fallback
                        roadmap.append({
                            "name": "📚 Learning Path",
                            "topics": [{"name": section, "completed": False}]
                        })
                    else:
                        section_name = section.get("name", "Untitled Section")
                        raw_topics = section.get("topics", [])
                        if isinstance(raw_topics, str):
                            raw_topics = [raw_topics]
                        
                        topics_list = []
                        for t in raw_topics:
                            if isinstance(t, str):
                                topics_list.append({"name": clean_topic_name(t), "completed": False})
                            else:
                                name = clean_topic_name(t.get("name") or t.get("topic") or str(t))
                                completed = bool(t.get("completed", False))
                                topics_list.append({"name": name, "completed": completed})
                        
                        roadmap.append({
                            "name": section_name,
                            "topics": topics_list
                        })

            # Save the new hierarchical roadmap
            await maybe_await(memory_agent.save_learning_path, current_user, roadmap)

        # 3️⃣ Extract flat completed topic names (for Home.jsx)
        completed_topics = []
        for section in roadmap:
            for topic in section.get("topics", []):
                if topic.get("completed"):
                    completed_topics.append(topic["name"])

        return {
            "roadmap": roadmap,               # ← hierarchical structure for LearningPath.jsx
            "completed_topics": completed_topics  # ← flat list for Home.jsx
        }

    except Exception as e:
        logger.exception("❌ Error generating roadmap")
        raise HTTPException(status_code=500, detail=f"Error generating roadmap: {str(e)}")


@router.post("/update", tags=["Learning Path"])
async def update_learning_path(payload: Dict[str, Any], current_user: str = Depends(get_current_user)):
    """
    Update hierarchical learning path.
    Expected payload: { "roadmap": [ { "name": "...", "topics": [ { "name": "...", "completed": true }, ... ] }, ... ] }
    """
    try:
        incoming_roadmap = payload.get("roadmap")
        if not isinstance(incoming_roadmap, list):
            raise HTTPException(status_code=400, detail="Invalid roadmap format. Expected array of sections.")

        normalized_roadmap = []
        completed_topics = []

        for section in incoming_roadmap:
            if not isinstance(section, dict) or "name" not in section:
                continue  # skip invalid
            
            section_name = section["name"]
            raw_topics = section.get("topics", [])
            if not isinstance(raw_topics, list):
                raw_topics = []

            normalized_topics = []
            for t in raw_topics:
                if isinstance(t, str):
                    topic_obj = {"name": clean_topic_name(t), "completed": False}
                else:
                    name = clean_topic_name(t.get("name") or t.get("topic") or str(t))
                    completed = bool(t.get("completed", False))
                    topic_obj = {"name": name, "completed": completed}
                
                normalized_topics.append(topic_obj)
                if topic_obj["completed"]:
                    completed_topics.append(topic_obj["name"])

            normalized_roadmap.append({
                "name": section_name,
                "topics": normalized_topics
            })

        # Save updated hierarchical path
        await maybe_await(memory_agent.save_learning_path, current_user, normalized_roadmap)

        # Compute overall progress
        total_topics = sum(len(sec["topics"]) for sec in normalized_roadmap)
        completed_count = len(completed_topics)
        progress = round((completed_count / total_topics) * 100, 2) if total_topics > 0 else 0

        # Trigger analytics
        if hasattr(analytics_agent, "generate_dashboard_metrics"):
            await maybe_await(analytics_agent.generate_dashboard_metrics, current_user, memory_agent)

        return {
            "message": "✅ Learning path updated successfully",
            "progress": progress,
            "completed_topics": completed_topics
        }

    except Exception as e:
        logger.exception("❌ Error updating learning path")
        raise HTTPException(status_code=500, detail=f"Error updating learning path: {str(e)}")