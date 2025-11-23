"""Ollama provider implementation for embeddings and chat."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import requests
from requests import RequestException


@dataclass(slots=True)
class OllamaProvider:
    base_url: str
    embed_model: str
    chat_model: str
    name: str = "ollama"

    def embed(self, text: str) -> List[float]:
        payload = {
            "model": self.embed_model,
            "prompt": text if text and text.strip() else " ",
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings", json=payload, timeout=60
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                raise RuntimeError(
                    f"Ollama model '{self.embed_model}' not found. "
                    f"Pull it with: ollama pull {self.embed_model}"
                ) from exc
            raise RuntimeError(
                f"Ollama embedding request failed: {exc.response.status_code if exc.response else 'unknown'}"
            ) from exc
        except RequestException as exc:  # connection/refused/timeouts etc.
            raise RuntimeError(
                f"Ollama embedding provider not reachable at {self.base_url}. "
                "Ensure ollama is running and OLLAMA_URL is correct."
            ) from exc

        data = response.json()
        return data["embedding"]

    def chat(self, prompt: str, **kwargs: Any) -> str:
        body: Dict[str, Any] = {
            "model": self.chat_model,
            "prompt": prompt,
            "stream": False,
        }
        body.update(kwargs)
        try:
            response = requests.post(
                f"{self.base_url}/api/generate", json=body, timeout=120
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                raise RuntimeError(
                    f"Ollama model '{self.chat_model}' not found. "
                    f"Pull it with: ollama pull {self.chat_model}"
                ) from exc
            raise RuntimeError(
                f"Ollama chat request failed: {exc.response.status_code if exc.response else 'unknown'}"
            ) from exc
        except RequestException as exc:
            raise RuntimeError(
                f"Ollama chat provider not reachable at {self.base_url}. "
                "Ensure ollama is running and OLLAMA_URL is correct."
            ) from exc

        data = response.json()
        return data.get("response", "")


def embed_ollama(text: str) -> List[float]:
    """Convenience function for embedding via Ollama with default settings."""
    from pjs_neo_rag.config import settings  # local import to avoid cycles

    provider = OllamaProvider(
        base_url=settings.OLLAMA_URL,
        embed_model=settings.OLLAMA_EMBED_MODEL,
        chat_model=settings.OLLAMA_CHAT_MODEL,
    )
    return provider.embed(text)
