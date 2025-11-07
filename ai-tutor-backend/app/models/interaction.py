# app/models/interaction.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.database.base import Base

class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"))
    type = Column(String(30), nullable=False)  # chat, quiz_submit, hint_used, explanation_view
    topic = Column(String(100))
    user_input = Column(Text)
    agent_response = Column(Text)
    extra_data = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="interactions")
    session = relationship("LearningSession", back_populates="interactions")
