# data/scripts/populate_sample_content.py
import asyncio
from pathlib import Path
from app.services.llm_service import llm_service
from app.utils.logger import get_logger

logger = get_logger("populate_content")

TOPICS = [
    ("Artificial Intelligence", "beginner", "simple"),
    ("Neural Networks", "intermediate", "technical"),
    ("Reinforcement Learning", "advanced", "tutorial"),
]

async def populate_explanations():
    base_dir = Path("data/content/explanation")
    base_dir.mkdir(parents=True, exist_ok=True)

    for topic, level, style in TOPICS:
        logger.info(f"📘 Generating explanation for {topic} ({level})...")
        explanation = await llm_service.explain(topic, level, style)
        file_path = base_dir / f"{topic.replace(' ', '_')}.json"

        file_path.write_text(
            f'{{"topic": "{topic}", "level": "{level}", "style": "{style}", "content": "{explanation}"}}',
            encoding="utf-8"
        )
        logger.info(f"✅ Saved explanation: {file_path}")

if __name__ == "__main__":
    logger.info("🚀 Populating sample explanations...")
    asyncio.run(populate_explanations())
    logger.info("✅ Sample explanations populated successfully.")
