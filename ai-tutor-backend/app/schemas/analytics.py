# app/schemas/analytics.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class PerformanceRecordBase(BaseModel):
    topic: str
    score: float = Field(..., ge=0.0, le=1.0)
    total_questions: Optional[int] = None
    correct_answers: Optional[int] = None
    time_spent_seconds: int = 0
    attempts: int = 1
    mistakes: List[str] = Field(default_factory=list)


class PerformanceRecordResponse(PerformanceRecordBase):
    id: int
    user_id: int
    quiz_id: Optional[int] = None
    recorded_at: datetime

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    topic: str
    action: str  # e.g., "revise", "practice", "explore next"
    reason: str


class AnalyticsDashboardResponse(BaseModel):
    average_score: float
    total_topics_covered: int
    knowledge_gaps: List[str]
    strong_areas: List[str]
    recent_performance: List[PerformanceRecordResponse] = Field(default_factory=list)
    recommendations: List[RecommendationResponse] = Field(default_factory=list)
    progress_timeline: List[Dict[str, Any]] = Field(default_factory=list)
