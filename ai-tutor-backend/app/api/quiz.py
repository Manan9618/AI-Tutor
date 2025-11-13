# app/api/quiz.py
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import sqlite3
import logging
from pathlib import Path

from .auth import get_current_user
from app.agents.quiz_agent import quiz_agent
from app.agents.memory_agent import memory_agent

router = APIRouter()
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "ai_tutor.db"


class QuizQuestion(BaseModel):
    id: int
    question: str
    options: Optional[Dict[str, str]] = None  # for MCQ
    answer: str
    type: str


class QuizResponse(BaseModel):
    quiz_id: int
    topic: str
    level: str
    num_questions: int
    questions: List[QuizQuestion]


class SubmitAnswers(BaseModel):
    answers: Dict[str, str]  # question_id -> answer (string keys)


class QuizHistoryItem(BaseModel):
    quiz_id: int
    topic: str
    level: str
    score: float
    total_questions: int
    correct_answers: int
    date: str
    duration: str
    attempts: int


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/generate", response_model=QuizResponse)
async def generate_quiz(
    topic: str = Query(..., description="Topic for quiz"),
    num_questions: int = Query(5, ge=1, le=10),
    current_user: str = Depends(get_current_user)
):
    """Generate a quiz for the topic."""
    try:
        profile = memory_agent.get_profile(current_user)
        level = profile.get("level", "beginner")
        
        # ✅ Generate MCQs
        quiz = await quiz_agent.generate_quiz(topic, level, num_questions, mcq=True)

        # ✅ Return FULL structure expected by QuizResponse
        return QuizResponse(
            quiz_id=-1,  # Temporary ID (assigned on submit)
            topic=topic,
            level=level,
            num_questions=len(quiz),
            questions=[
                QuizQuestion(
                    id=q["id"],
                    question=q["question"],
                    options=q.get("options", {}),
                    answer=q["answer"],
                    type=q["type"]
                )
                for q in quiz
            ]
        )
    except Exception as e:
        logger.error(f"Quiz generation failed for user {current_user}, topic {topic}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate quiz")


@router.post("/submit")
async def submit_quiz(
    topic: str = Query(..., description="Topic of the quiz"),
    answers: SubmitAnswers = Body(...),
    current_user: str = Depends(get_current_user)
):
    """Submit answers for a quiz."""
    try:
        profile = memory_agent.get_profile(current_user)
        level = profile.get("level", "beginner")
        num_questions = len(answers.answers)

        # ✅ Generate quiz
        quiz = await quiz_agent.generate_quiz(topic, level, num_questions)
        score, feedback = await quiz_agent.score_quiz(quiz, answers.answers)

        # ✅ Calculate correct answers — FIX: use answers.answers.get()
        correct_count = sum(
            1 for q in quiz 
            if answers.answers.get(str(q["id"]), "").strip().upper() == q["answer"].upper()
        )

        # ✅ Save to DB
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR IGNORE INTO quizzes (topic_id, title, level, num_questions, created_at)
                    VALUES (?, ?, ?, ?, datetime('now'))
                """, (topic, topic, level, num_questions))

                cursor.execute("SELECT id FROM quizzes WHERE title = ? AND level = ? ORDER BY created_at DESC LIMIT 1", (topic, level))
                quiz_row = cursor.fetchone()
                if not quiz_row:
                    raise Exception("Failed to retrieve quiz ID after insert")
                quiz_id = quiz_row['id']

                for q in quiz:
                    cursor.execute("""
                        INSERT INTO questions (
                            quiz_id, text, type, correct_answer, explanation, points, hint
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        quiz_id,
                        q["question"],
                        q["type"],
                        q["answer"],
                        "",
                        1,
                        ""
                    ))

                cursor.execute("""
                    INSERT INTO performance_records (
                        user_id, topic, quiz_id, score, total_questions, 
                        correct_answers, time_spent_seconds, attempts, mistakes, recorded_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    current_user,
                    topic,
                    quiz_id,
                    score,
                    num_questions,
                    correct_count,
                    0,
                    1,
                    "{}",
                ))
                conn.commit()

        except Exception as db_err:
            logger.error(f"Failed to save quiz result to DB: {db_err}")

        memory_agent.update_performance(current_user, topic, score)
        new_level = quiz_agent.adjust_difficulty(level, score)
        memory_agent.update_profile(current_user, "level", new_level)

        return {
            "score": round(score * 100, 2),
            "feedback": feedback,
            "quiz_id": quiz_id
        }

    except Exception as e:
        logger.error(f"Quiz submission failed for user {current_user}, topic {topic}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process quiz submission")


@router.get("/history")
async def get_quiz_history(
    current_user: str = Depends(get_current_user)
):
    """
    Get quiz history for the current user.
    Joins performance_records with quizzes and counts questions.
    Returns { "quizzes": [...] } to match frontend expectation.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.id AS performance_id,
                    p.user_id,
                    p.topic,
                    p.quiz_id,
                    p.score,
                    p.total_questions,
                    p.correct_answers,
                    p.time_spent_seconds,
                    p.attempts,
                    p.recorded_at,
                    q.title AS quiz_title,
                    q.level,
                    q.num_questions AS quiz_num_questions
                FROM performance_records p
                JOIN quizzes q ON p.quiz_id = q.id
                WHERE p.user_id = ?
                ORDER BY p.recorded_at DESC
                LIMIT 10
            """, (current_user,))

            rows = cursor.fetchall()

        history = []
        for row in rows:
            seconds = row['time_spent_seconds'] or 0
            minutes = int(seconds // 60)
            duration = f"{minutes} min" if minutes > 0 else "Less than 1 min"

            history.append(QuizHistoryItem(
                quiz_id=row['quiz_id'],
                topic=row['topic'],
                level=row['level'],
                score=row['score'],
                total_questions=row['total_questions'],
                correct_answers=row['correct_answers'],
                date=row['recorded_at'],
                duration=duration,
                attempts=row['attempts']
            ))

        # ✅ WRAP in { "quizzes": [...] } — matches Home.jsx expectation
        return {"quizzes": history}

    except Exception as e:
        logger.error(f"Failed to fetch quiz history for {current_user}: {e}")
        return {"quizzes": []}