# app/utils/validators.py
import re
from fastapi import HTTPException, status
from typing import Literal, Dict

LearningLevel = Literal["beginner", "intermediate", "advanced"]
LearningStyle = Literal["visual", "auditory", "kinesthetic", "text"]

def validate_topic_name(topic: str) -> str:
    """
    Validate topic name: 3–50 chars, alphanumeric, spaces, hyphens, underscores.
    """
    if not topic or len(topic.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic name must be at least 3 characters long."
        )
    if not re.match(r"^[a-zA-Z0-9\s\-_]+$", topic):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic name contains invalid characters."
        )
    return topic.strip().lower()

def validate_learning_level(level: str) -> LearningLevel:
    """
    Validate learning level.
    """
    valid_levels: set[LearningLevel] = {"beginner", "intermediate", "advanced"}
    level_lower = level.lower()
    if level_lower not in valid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid level. Must be one of: {', '.join(valid_levels)}"
        )
    return level_lower  # type: ignore

def validate_learning_style(style: str) -> LearningStyle:
    """
    Validate learning style.
    """
    valid_styles: set[LearningStyle] = {"visual", "auditory", "kinesthetic", "text"}
    style_lower = style.lower()
    if style_lower not in valid_styles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}"
        )
    return style_lower  # type: ignore

def validate_quiz_answer_format(answers: Dict[int, str]):
    """
    Validate quiz answer submission format.
    Example: {1: "A", 2: "C", 3: "B"}
    """
    if not isinstance(answers, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answers must be an object mapping question_id: answer"
        )
    for qid, ans in answers.items():
        if not isinstance(qid, int) or not isinstance(ans, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format for question {qid}. Expected int:str pair."
            )
        if len(ans.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Answer for question {qid} cannot be empty."
            )
    return answers
