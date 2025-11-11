# # app/api/learner.py
# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from typing import Dict, Optional

# from .auth import get_current_user
# from app.api import memory_agent

# # ✅ FIXED: No prefix or tags here — added in main.py
# router = APIRouter()


# class LearnerProfile(BaseModel):
#     age: Optional[int] = None
#     grade: Optional[int] = None
#     style: Optional[str] = None
#     level: Optional[str] = None


# @router.get("/profile", response_model=Dict)
# async def get_profile(current_user: str = Depends(get_current_user)):
#     """
#     Retrieve the learner profile from memory.
#     """
#     profile = memory_agent.get_profile(current_user)
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     return profile


# @router.put("/profile")
# async def update_profile(profile_update: LearnerProfile, current_user: str = Depends(get_current_user)):
#     """
#     Update fields in the learner profile. Only provided fields are updated.
#     """
#     for key, value in profile_update.dict(exclude_unset=True).items():
#         memory_agent.update_profile(current_user, key, value)
#     return {"message": "Profile updated successfully"}


# # ✅ NEW ENDPOINT: Learner progress
# @router.get("/progress")
# async def get_learner_progress(current_user: str = Depends(get_current_user)):
#     """
#     Returns user's current learning progress.
#     Replace mock data with real logic later.
#     """
#     progress_data = memory_agent.get_progress(current_user)
#     if not progress_data:
#         progress_data = {
#             "completed_topics": 7,
#             "total_topics": 20,
#             "percentage": 35,
#         }

#     return {
#         "username": current_user,
#         "progress": progress_data,
#         "message": "Progress data retrieved successfully"
#     }


# app/api/learner.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
from app.agents.memory_agent import MemoryAgent

from .auth import get_current_user

memory_agent = MemoryAgent()

router = APIRouter()


# =============== REQUEST MODELS ===============
class ProfileUpdateRequest(BaseModel):
    # Personal info
    name: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None

    # Learning preferences
    learningStyle: Optional[str] = None
    difficultyLevel: Optional[str] = None
    dailyGoal: Optional[str] = None
    language: Optional[str] = None

    # Notification & UI settings
    emailNotifications: Optional[bool] = None
    pushNotifications: Optional[bool] = None
    weeklyReports: Optional[bool] = None
    achievementAlerts: Optional[bool] = None
    theme: Optional[str] = None


# =============== MOCK / DEFAULT DATA ===============
def get_default_profile(user_id: str) -> Dict[str, Any]:
    return {
        "id": user_id,
        "name": "Learner",
        "email": f"{user_id}@example.com",
        "location": "Unknown",
        "bio": "Passionate about learning new things!",
        "joinedDate": "January 2024",
        "level": "Beginner",
        "xp": 0,
        "nextLevelXp": 1000,
        "learningStyle": "Visual",
        "difficultyLevel": "Intermediate",
        "dailyGoal": "30 minutes",
        "language": "English",
        "emailNotifications": True,
        "pushNotifications": False,
        "weeklyReports": True,
        "achievementAlerts": True,
        "theme": "System",
    }

def get_mock_progress() -> Dict[str, Any]:
    return {
        "totalStudyTime": "47h 23m",
        "topicsMastered": 23,
        "quizAverage": 87,
        "currentStreak": 12,
        "coursesCompleted": 3,
        "accuracy": 89,
    }

def get_mock_achievements() -> List[Dict[str, Any]]:
    return [
        {"title": "First Steps", "description": "Complete your first learning session", "date": "Jan 15, 2024", "earned": True, "icon": "🎯"},
        {"title": "Week Warrior", "description": "Study for 7 consecutive days", "date": "Feb 3, 2024", "earned": True, "icon": "🔥"},
        {"title": "Quiz Master", "description": "Score 100% on 5 quizzes", "date": "Feb 28, 2024", "earned": True, "icon": "🏆"},
        {"title": "Knowledge Seeker", "description": "Explore 50 different topics", "progress": 68, "icon": "📚"},
        {"title": "Chat Champion", "description": "Complete 100 chat sessions", "progress": 45, "icon": "💬"},
        {"title": "Perfect Month", "description": "Study every day for a month", "progress": 23, "icon": "⭐"},
    ]


# =============== ROUTES ===============
@router.get("/profile", response_model=Dict[str, Any])
async def get_profile(current_user: str = Depends(get_current_user)):
    """
    Retrieve the full learner profile with progress and achievements.
    """
    try:
        # Safely get profile — may be None
        base_profile = memory_agent.get_profile(current_user)
        logger.info(f"Raw profile from memory_agent: {base_profile}")

        if base_profile is None:
            # Create a fresh default profile
            base_profile = {}

        # Now safely merge with defaults
        full_profile = {**get_default_profile(current_user), **base_profile}

        progress = memory_agent.get_progress(current_user) or get_mock_progress()
        achievements = get_mock_achievements()

        return {
            "profile": full_profile,
            "progress": progress,
            "achievements": achievements,
        }

    except Exception as e:
        logger.error(f"Failed to load profile for user {current_user}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error loading profile")


@router.put("/profile", response_model=dict)
async def update_profile(
    update_data: ProfileUpdateRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Update learner profile fields.
    Only provided (non-null) fields are updated.
    """
    try:
        update_dict = update_data.dict(exclude_unset=True, exclude_none=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        for key, value in update_dict.items():
            memory_agent.update_profile(current_user, key, value)

        return {"message": "Profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


@router.get("/progress", response_model=Dict[str, Any])
async def get_learner_progress(current_user: str = Depends(get_current_user)):
    """
    [Legacy] Get progress only — kept for backward compatibility.
    Prefer using /profile for full data.
    """
    progress = memory_agent.get_progress(current_user) or get_mock_progress()
    return {
        "username": current_user,
        "progress": progress,
        "message": "Progress data retrieved successfully"
    }