# data/scripts/rebuild_embeddings.py
import json
from pathlib import Path
from app.utils.logger import get_logger
from app.utils.embeddings import embed_text, batch_embed

logger = get_logger("rebuild_embeddings")


def rebuild_all_embeddings(output_dir: str = "data/content/embeddings"):
    """
    Rebuild embeddings for all explanations in data/content/explanation
    and save them as JSON files for later use.
    """
    explanation_dir = Path("data/content/explanation")
    embed_dir = Path(output_dir)
    embed_dir.mkdir(parents=True, exist_ok=True)

    if not explanation_dir.exists():
        logger.warning("⚠️ No explanation directory found. Run populate_sample_content.py first.")
        return

    logger.info("🧠 Rebuilding embeddings for explanations...")

    for file in explanation_dir.glob("*.json"):
        try:
            # Read explanation content
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            text_to_embed = f"{data.get('topic', '')}\n{data.get('content', '')}"
            embedding = embed_text(text_to_embed)

            # Save embedding
            output_file = embed_dir / f"{file.stem}_embedding.json"
            with open(output_file, "w", encoding="utf-8") as ef:
                json.dump(
                    {
                        "topic": data.get("topic"),
                        "embedding": embedding,
                    },
                    ef,
                    ensure_ascii=False,
                    indent=2,
                )

            logger.info(f"✅ Embedded and saved: {output_file.name}")

        except Exception as e:
            logger.error(f"❌ Error embedding file {file.name}: {e}")

    logger.info("🏁 All embeddings rebuilt successfully.")


if __name__ == "__main__":
    rebuild_all_embeddings()
