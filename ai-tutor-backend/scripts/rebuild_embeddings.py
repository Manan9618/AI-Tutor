# scripts/rebuild_embeddings.py
import json
from pathlib import Path
from app.utils.logger import get_logger
from app.utils.embeddings import embed_text

logger = get_logger("rebuild_embeddings")

def rebuild_all_embeddings(output_dir: str = "data/content/embeddings"):
    explanation_dir = Path("data/content/explanation")
    embed_dir = Path(output_dir)
    embed_dir.mkdir(parents=True, exist_ok=True)

    if not explanation_dir.exists():
        logger.warning("⚠️ No explanations found to embed.")
        return

    logger.info("🧠 Rebuilding embeddings...")
    for file in explanation_dir.glob("*.json"):
        try:
            data = json.load(open(file, encoding="utf-8"))
            text_to_embed = f"{data.get('topic', '')}\n{data.get('content', '')}"
            embedding = embed_text(text_to_embed)

            out_path = embed_dir / f"{file.stem}_embedding.json"
            json.dump({"topic": data.get("topic"), "embedding": embedding}, open(out_path, "w", encoding="utf-8"), indent=2)
            logger.info(f"✅ Embedded: {file.stem}")

        except Exception as e:
            logger.error(f"❌ Error processing {file.name}: {e}")

    logger.info("🏁 Embedding rebuild complete.")


if __name__ == "__main__":
    rebuild_all_embeddings()
