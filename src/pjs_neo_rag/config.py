"""Centralized configuration management for pjs-neo-rag."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Check for password in environment first, before loading .env
_password_from_env = os.getenv("NEO4J_PASSWORD")

# Load .env file (won't override existing environment variables)
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Neo4j connection
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    # Password prioritizes real environment variable over .env
    NEO4J_PASSWORD: str = _password_from_env or os.getenv("NEO4J_PASSWORD", "")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # Ollama embedding service
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
    EMBEDDER_MODEL: str = os.getenv("EMBEDDER_MODEL", "bge-m3")
    EMBED_DIM: int = int(os.getenv("EMBED_DIM", "1024"))

    # Chunking parameters
    CHUNK_TOKENS: int = int(os.getenv("CHUNK_TOKENS", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    # Source documents directory
    SOURCE_DIR: Path = Path(os.getenv("SOURCE_DIR", "./corpus")).expanduser().resolve()

    # API configuration
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    def validate(self) -> None:
        """Validate critical settings."""
        if not self.NEO4J_PASSWORD:
            raise ValueError("NEO4J_PASSWORD must be set in .env file")
        if self.EMBED_DIM <= 0:
            raise ValueError(f"EMBED_DIM must be positive, got {self.EMBED_DIM}")


# Singleton instance
settings = Settings()
