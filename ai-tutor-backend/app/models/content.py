# app/models/content.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    subject = Column(String(50), default="general")
    difficulty = Column(Integer, default=1)
    prerequisites = Column(JSON, default=list)
    tags = Column(JSON, default=list)

    explanations = relationship("Explanation", back_populates="topic", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="topic", cascade="all, delete-orphan")


class Explanation(Base):
    __tablename__ = "explanations"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    level = Column(String(20), default="beginner")
    style = Column(String(20), default="visual")
    content = Column(Text, nullable=False)
    examples = Column(JSON, default=list)

    topic = relationship("Topic", back_populates="explanations")
    media = relationship("Media", back_populates="explanation", cascade="all, delete-orphan")


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    explanation_id = Column(Integer, ForeignKey("explanations.id"), nullable=False)
    type = Column(String(20), nullable=False)
    url = Column(String(500), nullable=False)
    alt_text = Column(String(200))

    explanation = relationship("Explanation", back_populates="media")
