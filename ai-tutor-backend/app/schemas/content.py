# app/schemas/content.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class TopicBase(BaseModel):
    name: str = Field(..., max_length=100)
    subject: Optional[str] = "general"
    difficulty: int = Field(1, ge=1, le=5)
    prerequisites: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class TopicCreate(TopicBase):
    pass


class TopicResponse(TopicBase):
    id: int

    class Config:
        from_attributes = True


class MediaBase(BaseModel):
    type: str = Field(..., pattern="^(image|video|audio|diagram)$")
    url: str = Field(..., max_length=500)
    alt_text: Optional[str] = None


class MediaCreate(MediaBase):
    explanation_id: int


class MediaResponse(MediaBase):
    id: int
    explanation_id: int

    class Config:
        from_attributes = True


class ExplanationBase(BaseModel):
    topic_id: int
    level: str = Field("beginner", pattern="^(beginner|intermediate|advanced)$")
    style: str = Field("visual", pattern="^(visual|auditory|text)$")
    content: str
    examples: List[Dict[str, Any]] = Field(default_factory=list)


class ExplanationCreate(ExplanationBase):
    pass


class ExplanationResponse(ExplanationBase):
    id: int
    media: List[MediaResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Fix forward refs
ExplanationResponse.model_rebuild()
