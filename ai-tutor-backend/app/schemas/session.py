# app/schemas/session.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LearningSessionBase(BaseModel):
    user_id: int
    current_topic: Optional[str] = None
    roadmap: List[str] = Field(default_factory=list)
    current_idx: int = 0
    status: str = Field("active", pattern="^(active|paused|completed)$")


class LearningSessionCreate(LearningSessionBase):
    pass


class LearningSessionResponse(LearningSessionBase):
    id: int
    started_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionStateResponse(BaseModel):
    session_id: int
    current_topic: Optional[str]
    explanation: Optional[str]
    quiz: Optional[List[dict]]
    score: Optional[float]
    feedback: Optional[str]
    recommendations: Optional[str]
    finished: bool = False
