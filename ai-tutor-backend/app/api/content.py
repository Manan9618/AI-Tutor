# app/api/content.py
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from .auth import get_current_user
from app.api import explanation_agent, memory_agent

router = APIRouter()


class ExplanationResponse(BaseModel):
    explanation: str


@router.get("/explain", response_model=ExplanationResponse)
async def get_explanation(
    topic: str = Query(..., description="Topic to explain"),
    current_user: str = Depends(get_current_user)
):
    """
    Return an explanation for a topic tailored to the user's profile (level, style).
    """
    profile = memory_agent.get_profile(current_user)
    level = profile.get("level", "beginner")
    style = profile.get("style", "visual")
    explanation = explanation_agent.explain_concept(topic, level, style)
    return {"explanation": explanation}