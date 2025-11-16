"""Centralized configuration management for pjs-neo-rag."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Preserve passwords already injected via environment variables
_password_from_env = os.getenv("NEO4J_PASSWORD")

# Load .env (does not override existing environment variables)
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    ALLOWED_PROVIDERS = {"ollama", "vllm", "lmstudio"}

    def __init__(self) -> None:
        # Neo4j connection
        self.NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
        self.NEO4J_PASSWORD = _password_from_env or os.getenv("NEO4J_PASSWORD", "")
        self.NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

        # Provider selection
        embed_provider = os.getenv("EMBED_PROVIDER", "ollama").strip().lower()
        chat_provider = os.getenv("CHAT_PROVIDER", "").strip().lower()
        self.EMBED_PROVIDER = embed_provider or "ollama"
        self.CHAT_PROVIDER = chat_provider or self.EMBED_PROVIDER

        # Service endpoints
        self.OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
        self.VLLM_URL = os.getenv("VLLM_URL", "http://127.0.0.1:8001")
        self.LMSTUDIO_URL = os.getenv("LMSTUDIO_URL", "http://127.0.0.1:1234")

        # Provider-specific embedding models and dimensions
        self.OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "bge-m3")
        self.VLLM_EMBED_MODEL = os.getenv("VLLM_EMBED_MODEL", "BAAI/bge-m3")
        self.LMSTUDIO_EMBED_MODEL = os.getenv(
            "LMSTUDIO_EMBED_MODEL", "nomic-ai/nomic-embed-text-v1.5"
        )
        self.OLLAMA_EMBED_DIM = int(os.getenv("OLLAMA_EMBED_DIM", "1024"))
        self.VLLM_EMBED_DIM = int(os.getenv("VLLM_EMBED_DIM", "1024"))
        self.LMSTUDIO_EMBED_DIM = int(os.getenv("LMSTUDIO_EMBED_DIM", "768"))

        # Provider-specific chat models
        self.OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "mistral:7b")
        self.VLLM_CHAT_MODEL = os.getenv(
            "VLLM_CHAT_MODEL", "mistralai/Mistral-7B-Instruct-v0.2"
        )
        self.LMSTUDIO_CHAT_MODEL = os.getenv(
            "LMSTUDIO_CHAT_MODEL", "Meta-Llama-3-8B-Instruct"
        )

        # Resolved provider mappings
        self._provider_urls = {
            "ollama": self.OLLAMA_URL,
            "vllm": self.VLLM_URL,
            "lmstudio": self.LMSTUDIO_URL,
        }
        self._provider_embed_models = {
            "ollama": self.OLLAMA_EMBED_MODEL,
            "vllm": self.VLLM_EMBED_MODEL,
            "lmstudio": self.LMSTUDIO_EMBED_MODEL,
        }
        self._provider_embed_dims = {
            "ollama": self.OLLAMA_EMBED_DIM,
            "vllm": self.VLLM_EMBED_DIM,
            "lmstudio": self.LMSTUDIO_EMBED_DIM,
        }
        self._provider_chat_models = {
            "ollama": self.OLLAMA_CHAT_MODEL,
            "vllm": self.VLLM_CHAT_MODEL,
            "lmstudio": self.LMSTUDIO_CHAT_MODEL,
        }

        self.EMBED_URL = self._provider_urls.get(self.EMBED_PROVIDER, "")
        self.CHAT_URL = self._provider_urls.get(self.CHAT_PROVIDER, "")
        self.EMBED_MODEL = self._provider_embed_models.get(self.EMBED_PROVIDER, "")
        self.EMBED_DIM = self._provider_embed_dims.get(self.EMBED_PROVIDER, 0)
        self.CHAT_MODEL = self._provider_chat_models.get(self.CHAT_PROVIDER, "")

        # Chunking parameters
        self.CHUNK_TOKENS = int(os.getenv("CHUNK_TOKENS", "1000"))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

        # Source documents directory
        self.SOURCE_DIR = (
            Path(os.getenv("SOURCE_DIR", "./corpus")).expanduser().resolve()
        )

        # API configuration
        self.API_PORT = int(os.getenv("API_PORT", "8000"))

        self.validate()

    def validate(self) -> None:
        """Validate critical settings."""

        if not self.NEO4J_PASSWORD:
            raise ValueError(
                "NEO4J_PASSWORD must be set via environment variable or .env file"
            )

        for label, provider in (
            ("EMBED_PROVIDER", self.EMBED_PROVIDER),
            ("CHAT_PROVIDER", self.CHAT_PROVIDER),
        ):
            if provider not in self.ALLOWED_PROVIDERS:
                allowed = ", ".join(sorted(self.ALLOWED_PROVIDERS))
                raise ValueError(f"{label} must be one of: {allowed}")

        if not self.EMBED_URL:
            raise ValueError("Unable to resolve embedding service URL")
        if not self.CHAT_URL:
            raise ValueError("Unable to resolve chat service URL")
        if not self.EMBED_MODEL:
            raise ValueError("Embedding model not specified for selected provider")
        if not self.CHAT_MODEL:
            raise ValueError("Chat model not specified for selected provider")
        if self.EMBED_DIM <= 0:
            raise ValueError(f"EMBED_DIM must be positive, got {self.EMBED_DIM}")


# Singleton instance
settings = Settings()
