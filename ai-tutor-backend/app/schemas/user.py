# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: Optional[EmailStr] = None 
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=5, le=100)
    grade: Optional[int] = Field(None, ge=1, le=12)
    learning_style: Optional[str] = Field("visual", pattern="^(visual|auditory|kinesthetic)$")
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[int] = None
    learning_style: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearnerProfileUpdate(BaseModel):
    age: Optional[int] = None
    grade: Optional[int] = None
    learning_style: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class LearnerProfileResponse(BaseModel):
    age: Optional[int]
    grade: Optional[int]
    learning_style: str
    preferences: Dict[str, Any]
    level: Optional[str] = "beginner"  # derived metric

    class Config:
        from_attributes = True
