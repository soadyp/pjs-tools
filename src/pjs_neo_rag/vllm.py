"""vLLM provider implementation for embeddings and chat."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import requests
from requests import RequestException


@dataclass(slots=True)
class VLLMProvider:
    base_url: str
    embed_model: str
    chat_model: str
    name: str = "vllm"

    def embed(self, text: str) -> List[float]:
        payload = {
            "model": self.embed_model,
            "input": text if text and text.strip() else " ",
        }
        try:
            response = requests.post(
                f"{self.base_url}/v1/embeddings", json=payload, timeout=60
            )
            response.raise_for_status()
        except RequestException as exc:
            raise RuntimeError(
                f"vLLM embedding provider not reachable at {self.base_url}. "
                "Ensure vLLM is running and VLLM_URL is correct."
            ) from exc

        data = response.json()
        entries = data.get("data") or []
        if not entries:
            raise ValueError("vLLM embedding response missing data entries")
        return entries[0]["embedding"]

    def chat(self, prompt: str, **kwargs: Any) -> str:
        body: Dict[str, Any] = {
            "model": self.chat_model,
            "messages": [{"role": "user", "content": prompt}],
        }
        body.update(kwargs)
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions", json=body, timeout=120
            )
            response.raise_for_status()
        except RequestException as exc:
            raise RuntimeError(
                f"vLLM chat provider not reachable at {self.base_url}. "
                "Ensure vLLM is running and VLLM_URL is correct."
            ) from exc

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise ValueError("vLLM chat response missing choices")
        message = choices[0].get("message") or {}
        return message.get("content", "")
