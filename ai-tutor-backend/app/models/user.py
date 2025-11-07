# app/models/user.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from sqlalchemy.orm import relationship
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    age = Column(Integer)
    grade = Column(Integer)
    learning_style = Column(String(20), default="visual")  # visual, auditory, kinesthetic
    preferences = Column(JSON, default=dict)  # e.g., {"pace": "fast", "difficulty": "medium"}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sessions = relationship("LearningSession", back_populates="user", cascade="all, delete-orphan")
    performances = relationship("PerformanceRecord", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("InteractionLog", back_populates="user", cascade="all, delete-orphan")
