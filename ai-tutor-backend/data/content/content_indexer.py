"""
Handles embedding and vector indexing of content.
Integrates with app.services.embedding_service or Pinecone/Chroma.
"""
from app.config import settings
from app.services.embedding_service import EmbeddingService
from data.content.content_loader import load_text_files

async def build_content_index():
    """Embed and store all content into vector DB."""
    embedder = EmbeddingService(
        api_key=settings.OPENAI_API_KEY,
        model_name=settings.OPENAI_EMBEDDING_MODEL
    )

    texts = load_text_files()
    if not texts:
        print("⚠️ No content found to index.")
        return

    await embedder.index_texts(texts)
    print(f"✅ Indexed {len(texts)} documents successfully.")
