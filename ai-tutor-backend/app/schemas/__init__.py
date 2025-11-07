# app/schemas/__init__.py
from .user import (
    UserBase, UserCreate, UserUpdate, UserResponse,
    LearnerProfileUpdate, LearnerProfileResponse,
)
from .content import (
    TopicBase, TopicCreate, TopicResponse,
    ExplanationBase, ExplanationCreate, ExplanationResponse,
    MediaBase, MediaCreate, MediaResponse,
)
from .quiz import (
    QuizBase, QuizCreate, QuizResponse,
    QuestionBase, QuestionCreate, QuestionResponse,
    ChoiceBase, ChoiceCreate, ChoiceResponse,
    QuizSubmitRequest, QuizSubmitResponse,
)
from .session import (
    LearningSessionBase, LearningSessionCreate, LearningSessionResponse,
    SessionStateResponse,
)
from .analytics import (
    PerformanceRecordBase, PerformanceRecordResponse,
    AnalyticsDashboardResponse, RecommendationResponse,
)

__all__ = [
    # User
    "UserBase", "UserCreate", "UserUpdate", "UserResponse",
    "LearnerProfileUpdate", "LearnerProfileResponse",

    # Content
    "TopicBase", "TopicCreate", "TopicResponse",
    "ExplanationBase", "ExplanationCreate", "ExplanationResponse",
    "MediaBase", "MediaCreate", "MediaResponse",

    # Quiz
    "QuizBase", "QuizCreate", "QuizResponse",
    "QuestionBase", "QuestionCreate", "QuestionResponse",
    "ChoiceBase", "ChoiceCreate", "ChoiceResponse",
    "QuizSubmitRequest", "QuizSubmitResponse",

    # Session
    "LearningSessionBase", "LearningSessionCreate", "LearningSessionResponse",
    "SessionStateResponse",

    # Analytics
    "PerformanceRecordBase", "PerformanceRecordResponse",
    "AnalyticsDashboardResponse", "RecommendationResponse",
]
