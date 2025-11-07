# # app/api/__init__.py
# from fastapi import APIRouter

# # Import agent classes
# from app.agents import (
#     MemoryAgent,
#     ExplanationAgent,
#     PathGeneratorAgent,
#     QuizAgent,
#     ChatAgent,
#     AnalyticsAgent,
# )

# # Shared agent instances
# memory_agent = MemoryAgent()
# explanation_agent = ExplanationAgent(content_repo={})
# path_generator = PathGeneratorAgent(topics_graph={})
# quiz_agent = QuizAgent(question_bank={})
# chat_agent = ChatAgent()
# analytics_agent = AnalyticsAgent()

# # Import routers (after creating shared agents)
# from .auth import router as auth_router
# from .learner import router as learner_router
# from .learning_path import router as learning_path_router
# from .content import router as content_router
# from .quiz import router as quiz_router
# from .chat import router as chat_router
# from .analytics import router as analytics_router
# from .explanation import router as explanation_router  # ✅ NEW

# api_router = APIRouter()

# api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
# api_router.include_router(learner_router, prefix="/learner", tags=["learner"])
# api_router.include_router(learning_path_router, prefix="/learning-path", tags=["learning_path"])
# api_router.include_router(content_router, prefix="/content", tags=["content"])
# api_router.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
# api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
# api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
# api_router.include_router(explanation_router, prefix="/explanation", tags=["explanation"])  # ✅ NEW


# app/api/__init__.py
from fastapi import APIRouter

# Import agent classes
from app.agents import (
    MemoryAgent,
    ExplanationAgent,
    PathGeneratorAgent,
    QuizAgent,
    ChatAgent,
    AnalyticsAgent,
)

# Shared agent instances
# Use the same model_name for all agents to share the model efficiently
DEFAULT_MODEL = "google/gemma-2b-it"

print("🚀 Initializing agents...")

# Memory agent doesn't need heavy LLM, so initialize it first
memory_agent = MemoryAgent(model_name=DEFAULT_MODEL)

# All other agents will share the same model
explanation_agent = ExplanationAgent(content_repo={}, model_name=DEFAULT_MODEL)
path_generator = PathGeneratorAgent(topics_graph={}, model_name=DEFAULT_MODEL)
quiz_agent = QuizAgent(question_bank={}, model_name=DEFAULT_MODEL)
chat_agent = ChatAgent(model_name=DEFAULT_MODEL)
analytics_agent = AnalyticsAgent(model_name=DEFAULT_MODEL)

print("✅ All agents initialized successfully!")

# Import routers (after creating shared agents)
from .auth import router as auth_router
from .learner import router as learner_router
from .learning_path import router as learning_path_router
from .content import router as content_router
from .quiz import router as quiz_router
from .chat import router as chat_router
from .analytics import router as analytics_router
from .explanation import router as explanation_router

print("🔍 Importing auth router from:", auth_router)


api_router = APIRouter()

api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(learner_router, prefix="/learner", tags=["learner"])
api_router.include_router(learning_path_router, prefix="/learning-path", tags=["learning_path"])
api_router.include_router(content_router, prefix="/content", tags=["content"])
api_router.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(explanation_router, prefix="/explanations", tags=["explanation"])