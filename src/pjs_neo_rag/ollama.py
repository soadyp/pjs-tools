"""
Ollama API integration for embeddings and LLM interactions.
"""

import math
import requests
from pjs_neo_rag.config import settings


def embed_ollama(text: str):
    """
    Generate normalized embedding vector using Ollama.

    Args:
        text: Input text to embed

    Returns:
        Normalized embedding vector (list of floats)
    """
    if not text or not text.strip():
        text = " "
    r = requests.post(
        f"{settings.OLLAMA_URL}/api/embeddings",
        json={"model": settings.EMBEDDER_MODEL, "prompt": text},
        timeout=60,
    )
    r.raise_for_status()
    v = r.json()["embedding"]
    if len(v) != settings.EMBED_DIM:
        raise ValueError(f"Embedding dim {len(v)} != {settings.EMBED_DIM}")
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]
