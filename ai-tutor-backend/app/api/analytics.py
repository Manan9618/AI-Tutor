# app/api/analytics.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict

from .auth import get_current_user
from app.api import analytics_agent, memory_agent

router = APIRouter()


@router.get("/", tags=["analytics"])
async def analytics_root():
    """
    Root endpoint for analytics.
    This prevents 404 errors if someone accesses /api/analytics directly.
    """
    return {
        "message": "📊 Analytics API active. Use /recommendations or /dashboard for specific analytics data."
    }


@router.get("/recommendations", response_model=Dict, tags=["analytics"])
async def get_recommendations(current_user: str = Depends(get_current_user)):
    """
    Return LLM-generated personalized recommendations for the current user.
    """
    try:
        recommendations = analytics_agent.generate_recommendations(current_user, memory_agent)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.get("/dashboard", response_model=Dict, tags=["analytics"])
async def get_dashboard(current_user: str = Depends(get_current_user)):
    try:
        metrics = analytics_agent.generate_dashboard_metrics(current_user, memory_agent)

        # Include learning path progress if available
        learning_path = memory_agent.get_user_learning_path(current_user) or []
        completed = sum(1 for t in learning_path if t.get("completed"))
        total = len(learning_path)
        progress = round((completed / total) * 100, 2) if total > 0 else 0

        metrics.update({
            "learning_path_progress": progress,
            "completed_topics": completed,
            "total_topics": total
        })

        return metrics

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard metrics: {str(e)}")

@router.post("/update", tags=["analytics"])
async def update_analytics(data: dict, current_user: str = Depends(get_current_user)):
    """
    Update analytics when user performs actions (chat, topic, quiz).
    """
    try:
        action = data.get("action")
        topic = data.get("topic")

        if action == "chat":
            memory_agent.increment_chat(current_user)
        elif action == "topic_explored":
            memory_agent.increment_topic_explored(current_user, topic)
        elif action == "quiz_completed":
            memory_agent.increment_quiz_completed(current_user)

        # Always recompute dashboard
        dashboard = analytics_agent.generate_dashboard_metrics(current_user, memory_agent)
        return {"status": "success", "analytics": dashboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))