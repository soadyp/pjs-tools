"""Provider registry for embeddings and chat services."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, List, Protocol, runtime_checkable

from pjs_neo_rag.config import settings
from pjs_neo_rag.lmstudio import LMStudioProvider
from pjs_neo_rag.ollama import OllamaProvider
from pjs_neo_rag.vllm import VLLMProvider


@runtime_checkable
class AIProvider(Protocol):
    """Minimal interface shared by embedding/chat backends."""

    name: str

    def embed(self, text: str) -> List[float]:  # pragma: no cover - interface
        ...

    def chat(self, prompt: str, **kwargs: Any) -> str:  # pragma: no cover - interface
        ...


@lru_cache(maxsize=None)
def _provider_factory(name: str) -> AIProvider:
    if name == "ollama":
        return OllamaProvider(
            base_url=settings.OLLAMA_URL,
            embed_model=settings.OLLAMA_EMBED_MODEL,
            chat_model=settings.OLLAMA_CHAT_MODEL,
        )
    if name == "vllm":
        return VLLMProvider(
            base_url=settings.VLLM_URL,
            embed_model=settings.VLLM_EMBED_MODEL,
            chat_model=settings.VLLM_CHAT_MODEL,
        )
    if name == "lmstudio":
        return LMStudioProvider(
            base_url=settings.LMSTUDIO_URL,
            embed_model=settings.LMSTUDIO_EMBED_MODEL,
            chat_model=settings.LMSTUDIO_CHAT_MODEL,
        )
    raise ValueError(f"Unsupported AI provider '{name}'")


def get_embedding_provider() -> AIProvider:
    """Return the provider configured for embeddings."""

    return _provider_factory(settings.EMBED_PROVIDER)


def get_chat_provider() -> AIProvider:
    """Return the provider configured for chat generation."""

    return _provider_factory(settings.CHAT_PROVIDER)
