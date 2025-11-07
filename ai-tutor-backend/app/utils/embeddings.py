# app/utils/embeddings.py
from sentence_transformers import SentenceTransformer
from typing import List
from functools import lru_cache
import numpy as np

@lru_cache(maxsize=1)
def get_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Load and cache the SentenceTransformer model.
    Ensures the model is loaded once per app lifecycle.
    """
    return SentenceTransformer(model_name)

def embed_text(text: str, model_name: str = "all-MiniLM-L6-v2") -> List[float]:
    """
    Generate a single text embedding as a list of floats.
    """
    model = get_embedding_model(model_name)
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def batch_embed(
    texts: List[str],
    model_name: str = "all-MiniLM-L6-v2",
    batch_size: int = 32
) -> List[List[float]]:
    """
    Efficiently embed multiple texts in batches.
    """
    if not texts:
        return []
    model = get_embedding_model(model_name)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        normalize_embeddings=True
    )
    return embeddings.tolist()
