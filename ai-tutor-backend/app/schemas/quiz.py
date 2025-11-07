# app/schemas/quiz.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class ChoiceBase(BaseModel):
    text: str
    is_correct: bool = False


class ChoiceCreate(ChoiceBase):
    question_id: int


class ChoiceResponse(ChoiceBase):
    id: int
    question_id: int

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    text: str
    type: str = Field("mcq", pattern="^(mcq|short_answer|true_false)$")
    correct_answer: str
    explanation: Optional[str] = None
    points: int = 1
    hint: Optional[str] = None


class QuestionCreate(QuestionBase):
    quiz_id: int
    choices: List[ChoiceCreate] = Field(default_factory=list)


class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int
    choices: List[ChoiceResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    topic_id: int
    title: str = Field(..., max_length=200)
    level: str = "beginner"
    num_questions: int = Field(5, ge=1, le=20)


class QuizCreate(QuizBase):
    pass


class QuizResponse(QuizBase):
    id: int
    created_at: datetime
    questions: List[QuestionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# --- Quiz Submission ---
class QuizSubmitRequest(BaseModel):
    answers: Dict[int, str]  # question_id -> user_answer


class QuizSubmitResponse(BaseModel):
    score: float  # 0.0–1.0
    total_questions: int
    correct_answers: int
    feedback: str
    recommendations: Optional[str] = None
    next_level: Optional[str] = None


QuizResponse.model_rebuild()
