# app/api/learner.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)
from app.agents.memory_agent import MemoryAgent
from .auth import get_current_user

# Initialize agent and router
memory_agent = MemoryAgent()
router = APIRouter()

# Database path (adjust if your structure differs)
DB_PATH = Path(__file__).parent.parent / "data" / "ai_tutor.db"

def get_db_connection():
    """Get SQLite connection"""
    return sqlite3.connect(str(DB_PATH))


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


# =============== NEW: PROFILE STATS ENDPOINT ===============
@router.get("/profile-stats", response_model=Dict[str, Any])
async def get_profile_stats(current_user: str = Depends(get_current_user)):
    """
    Get accurate study time and current streak from database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Total study time (sum of completed sessions)
        cursor.execute("""
            SELECT COALESCE(SUM(duration_seconds), 0)
            FROM study_sessions
            WHERE user_id = ? AND end_time IS NOT NULL
        """, (current_user,))
        total_seconds = cursor.fetchone()[0] or 0

        # 2. Current streak (consecutive login days ending today)
        today = datetime.utcnow().date()
        cursor.execute("""
            SELECT login_date FROM user_logins
            WHERE user_id = ?
            ORDER BY login_date DESC
        """, (current_user,))
        
        dates = []
        for row in cursor.fetchall():
            try:
                dates.append(datetime.strptime(row[0], "%Y-%m-%d").date())
            except (ValueError, TypeError):
                continue  # Skip invalid dates

        # Calculate streak
        streak = 0
        expected = today
        for d in dates:
            if d == expected:
                streak += 1
                expected -= timedelta(days=1)
            elif d < expected:
                break  # Gap found

        conn.close()

        return {
            "total_study_time_seconds": total_seconds,
            "current_streak_days": streak
        }

    except Exception as e:
        logger.error(f"Error fetching profile stats for {current_user}: {e}")
        # Fallback to 0 if DB error occurs
        return {
            "total_study_time_seconds": 0,
            "current_streak_days": 0
        }


# =============== EXISTING ROUTES ===============
@router.get("/profile", response_model=Dict[str, Any])
async def get_profile(current_user: str = Depends(get_current_user)):
    """
    Retrieve the full learner profile with progress and achievements.
    """
    try:
        base_profile = memory_agent.get_profile(current_user)
        logger.info(f"Raw profile from memory_agent: {base_profile}")

        if base_profile is None:
            base_profile = {}

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
        logger.error(f"Profile update error for {current_user}: {e}")
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