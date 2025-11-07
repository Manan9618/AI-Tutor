# # app/api/quiz.py
# from fastapi import APIRouter, Depends, Query, Body
# from pydantic import BaseModel
# from typing import List, Dict

# from .auth import get_current_user
# from app.api import quiz_agent, memory_agent

# router = APIRouter()


# class QuizQuestion(BaseModel):
#     id: int
#     question: str


# class QuizResponse(BaseModel):
#     questions: List[QuizQuestion]


# class SubmitAnswers(BaseModel):
#     answers: Dict[int, str]  # question_id -> answer


# @router.get("/generate", response_model=QuizResponse)
# async def generate_quiz(
#     topic: str = Query(..., description="Topic for quiz"),
#     num_questions: int = Query(5, ge=1, le=10),
#     current_user: str = Depends(get_current_user)
# ):
#     """
#     Generate a quiz for the topic. Only returns question id and question text (no answers).
#     """
#     profile = memory_agent.get_profile(current_user)
#     level = profile.get("level", "beginner")
#     quiz = quiz_agent.generate_quiz(topic, level, num_questions)

#     # Return only id and question to the client
#     questions = [{"id": q["id"], "question": q["question"]} for q in quiz]
#     return {"questions": questions}


# @router.post("/submit")
# async def submit_quiz(
#     topic: str = Query(..., description="Topic of the quiz"),
#     answers: SubmitAnswers = Body(...),
#     current_user: str = Depends(get_current_user)
# ):
#     """
#     Submit answers for a quiz. For simplicity we re-generate the quiz (or you can store the quiz server-side).
#     Returns score and feedback.
#     """
#     profile = memory_agent.get_profile(current_user)
#     level = profile.get("level", "beginner")

#     # Re-generate the quiz with the same number of questions as submitted
#     quiz = quiz_agent.generate_quiz(topic, level, len(answers.answers))
#     score, feedback = quiz_agent.score_quiz(quiz, answers.answers)

#     # Update memory and possibly adjust level
#     memory_agent.update_performance(current_user, topic, score)
#     new_level = quiz_agent.adjust_difficulty(level, score)
#     memory_agent.update_profile(current_user, "level", new_level)

#     return {"score": score, "feedback": feedback}

# app/api/quiz.py
from fastapi import APIRouter, Depends, Query, Body
from pydantic import BaseModel
from typing import List, Dict
import sqlite3
from datetime import datetime

from .auth import get_current_user
from app.api import quiz_agent, memory_agent

router = APIRouter()

# Database path (adjust if needed)
DB_PATH = "app/data/ai_tutor.db"

class QuizQuestion(BaseModel):
    id: int
    question: str

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]

class SubmitAnswers(BaseModel):
    answers: Dict[int, str]  # question_id -> answer

class QuizHistoryItem(BaseModel):
    topic: str          # From quizzes.title
    level: str          # From quizzes.level
    score: int
    total: int
    date: str           # ISO formatted recorded_at
    duration: str       # Human-readable time spent (e.g., "5 min")
    attempts: int

def get_db_connection():
    """Get SQLite connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dict
    return conn

@router.get("/generate", response_model=QuizResponse)
async def generate_quiz(
    topic: str = Query(..., description="Topic for quiz"),
    num_questions: int = Query(5, ge=1, le=10),
    current_user: str = Depends(get_current_user)
):
    """
    Generate a quiz for the topic. Only returns question id and question text (no answers).
    """
    profile = memory_agent.get_profile(current_user)
    level = profile.get("level", "beginner")
    quiz = quiz_agent.generate_quiz(topic, level, num_questions)

    # Return only id and question to the client
    questions = [{"id": q["id"], "question": q["question"]} for q in quiz]
    return {"questions": questions}

@router.post("/submit")
async def submit_quiz(
    topic: str = Query(..., description="Topic of the quiz"),
    answers: SubmitAnswers = Body(...),
    current_user: str = Depends(get_current_user)
):
    """
    Submit answers for a quiz.
    - Re-generates the quiz to score it.
    - Saves performance record to database.
    - Updates user profile.
    Returns score and feedback.
    """
    profile = memory_agent.get_profile(current_user)
    level = profile.get("level", "beginner")

    # Re-generate the quiz with same number of questions
    quiz = quiz_agent.generate_quiz(topic, level, len(answers.answers))
    score, feedback = quiz_agent.score_quiz(quiz, answers.answers)

    # Save to performance_records
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First, check if a quiz exists for this topic/level/num_questions
        # If not, create one in quizzes table
        cursor.execute("""
            INSERT OR IGNORE INTO quizzes (topic_id, title, level, num_questions, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (topic, topic, level, len(answers.answers)))

        # Get the quiz_id
        cursor.execute("SELECT id FROM quizzes WHERE title = ? AND level = ?", (topic, level))
        quiz_row = cursor.fetchone()
        if not quiz_row:
            raise Exception("Failed to find or create quiz record")
        quiz_id = quiz_row['id']

        # Insert performance record
        cursor.execute("""
            INSERT INTO performance_records (
                user_id, quiz_id, score, total_questions, 
                time_spent_seconds, attempts, mistakes, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            current_user,
            quiz_id,
            score,
            len(answers.answers),
            0,  # You can pass actual time if available
            1,  # Assume 1 attempt for now
            "{}"  # Empty JSON for mistakes
        ))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error saving quiz result: {e}")
        # Continue anyway — don't block user experience

    # Update memory and adjust level
    memory_agent.update_performance(current_user, topic, score)
    new_level = quiz_agent.adjust_difficulty(level, score)
    memory_agent.update_profile(current_user, "level", new_level)

    return {"score": score, "feedback": feedback}

@router.get("/history", response_model=List[QuizHistoryItem])
async def get_quiz_history(
    current_user: str = Depends(get_current_user)
):
    """
    Get quiz history for the current user (last 10 quizzes).
    Joins performance_records with quizzes to get topic title and level.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                p.user_id,
                p.quiz_id,
                p.score,
                p.total_questions,
                p.time_spent_seconds,
                p.attempts,
                p.recorded_at,
                q.title AS topic,
                q.level
            FROM performance_records p
            JOIN quizzes q ON p.quiz_id = q.id
            WHERE p.user_id = ?
            ORDER BY p.recorded_at DESC
            LIMIT 10
        """, (current_user,))

        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            # Format duration
            seconds = row['time_spent_seconds']
            minutes = int(seconds // 60)
            duration = f"{minutes} min" if minutes > 0 else "Less than 1 min"

            history.append({
                "topic": row['topic'],
                "level": row['level'],
                "score": row['score'],
                "total": row['total_questions'],
                "date": row['recorded_at'],  # Already ISO format from SQLite
                "duration": duration,
                "attempts": row['attempts']
            })

        return history

    except Exception as e:
        print(f"Error fetching quiz history: {e}")
        return []  # Return empty list on error