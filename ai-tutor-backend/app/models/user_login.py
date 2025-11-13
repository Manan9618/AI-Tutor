# app/models/user_login.py
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from app.database.base import Base

class UserLogin(Base):
    __tablename__ = "user_logins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    login_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # Enforce one login per user per day
        {"sqlite_autoincrement": True}
    )