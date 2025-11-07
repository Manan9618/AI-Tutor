# scripts/manage_questions.py
import asyncio
import json
from pathlib import Path
from app.services.llm_service import llm_service
from app.utils.logger import get_logger

logger = get_logger("manage_questions")

QUESTION_FILE = Path("data/questions/question_bank.json")

async def generate_quiz(topic: str, level: str = "beginner", num: int = 5):
    """Generate quiz questions using the LLM."""
    logger.info(f"🧠 Generating quiz for {topic} ({level})...")
    questions = await llm_service.generate_quiz(topic=topic, level=level, num=num)

    if questions:
        QUESTION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(QUESTION_FILE, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Quiz saved to {QUESTION_FILE}")
    else:
        logger.warning("⚠️ No quiz generated. Please check LLM configuration.")

if __name__ == "__main__":
    asyncio.run(generate_quiz("Machine Learning", "intermediate", 5))
