# app/models/session.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.database.base import Base

class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    current_topic = Column(String(100))
    roadmap = Column(JSON, default=list)
    current_idx = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active, paused, completed

    user = relationship("User", back_populates="sessions")
    interactions = relationship("InteractionLog", back_populates="session", cascade="all, delete-orphan")
