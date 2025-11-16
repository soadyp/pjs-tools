"""Embedding helper using the configured AI provider."""

from __future__ import annotations

import math
from typing import List

from pjs_neo_rag.ai_providers import get_embedding_provider
from pjs_neo_rag.config import settings


def _normalize_vector(vec: List[float]) -> List[float]:
    """Return an L2-normalized copy of the vector."""
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def embed_vector(text: str) -> List[float]:
    """Generate an embedding vector from the configured provider."""
    provider = get_embedding_provider()
    clean_text = text if text and text.strip() else " "

    vector = provider.embed(clean_text)

    if len(vector) != settings.EMBED_DIM:
        raise ValueError(
            f"Embedding dimension {len(vector)} does not match expected {settings.EMBED_DIM}"
        )

    return _normalize_vector(vector)
