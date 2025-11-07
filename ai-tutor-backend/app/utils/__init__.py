# app/utils/__init__.py
from .logger import get_logger, setup_logging
from .embeddings import get_embedding_model, embed_text, batch_embed
from .prompts import (
    EXPLANATION_PROMPT,
    QUIZ_GENERATION_PROMPT,
    CHAT_GUIDANCE_PROMPT,
    RAG_ENHANCEMENT_PROMPT,
)
from .validators import (
    validate_topic_name,
    validate_learning_level,
    validate_learning_style,
    validate_quiz_answer_format,
)

__all__ = [
    "get_logger", "setup_logging",
    "get_embedding_model", "embed_text", "batch_embed",
    "EXPLANATION_PROMPT", "QUIZ_GENERATION_PROMPT",
    "CHAT_GUIDANCE_PROMPT", "RAG_ENHANCEMENT_PROMPT",
    "validate_topic_name", "validate_learning_level",
    "validate_learning_style", "validate_quiz_answer_format",
]
