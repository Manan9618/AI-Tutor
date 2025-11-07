# app/api/learner.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

from .auth import get_current_user
from app.api import memory_agent

# ✅ FIXED: No prefix or tags here — added in main.py
router = APIRouter()


class LearnerProfile(BaseModel):
    age: Optional[int] = None
    grade: Optional[int] = None
    style: Optional[str] = None
    level: Optional[str] = None


@router.get("/profile", response_model=Dict)
async def get_profile(current_user: str = Depends(get_current_user)):
    """
    Retrieve the learner profile from memory.
    """
    profile = memory_agent.get_profile(current_user)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/profile")
async def update_profile(profile_update: LearnerProfile, current_user: str = Depends(get_current_user)):
    """
    Update fields in the learner profile. Only provided fields are updated.
    """
    for key, value in profile_update.dict(exclude_unset=True).items():
        memory_agent.update_profile(current_user, key, value)
    return {"message": "Profile updated successfully"}


# ✅ NEW ENDPOINT: Learner progress
@router.get("/progress")
async def get_learner_progress(current_user: str = Depends(get_current_user)):
    """
    Returns user's current learning progress.
    Replace mock data with real logic later.
    """
    progress_data = memory_agent.get_progress(current_user)
    if not progress_data:
        progress_data = {
            "completed_topics": 7,
            "total_topics": 20,
            "percentage": 35,
        }

    return {
        "username": current_user,
        "progress": progress_data,
        "message": "Progress data retrieved successfully"
    }