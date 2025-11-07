# app/models/performance.py
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.database.base import Base

class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(100), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    score = Column(Float, nullable=False)
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    time_spent_seconds = Column(Integer, default=0)
    attempts = Column(Integer, default=1)
    mistakes = Column(JSON, default=list)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="performances")
    quiz = relationship("Quiz")
