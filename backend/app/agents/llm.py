"""Provider-agnostic LLM client for the agentic layer.

Supports Hugging Face (free Inference API), Groq (free, OpenAI-compatible),
and Ollama (local). If no provider/key is configured, or a call fails, it
returns None and the agents fall back to their deterministic templates -- so
the whole product works end-to-end with ZERO keys and never breaks on stage.
"""
from typing import Optional

import requests

from app.config import settings

TIMEOUT = 30


class LLMClient:
    def __init__(self) -> None:
        self.provider = settings.LLM_PROVIDER

    def available(self) -> bool:
        if self.provider == "huggingface":
            return bool(settings.HF_API_TOKEN)
        if self.provider == "groq":
            return bool(settings.GROQ_API_KEY)
        if self.provider == "ollama":
            return True
        return False  # "template" or unknown -> deterministic mode

    def info(self) -> dict:
        model = {"huggingface": settings.HF_MODEL, "groq": settings.GROQ_MODEL,
                 "ollama": settings.OLLAMA_MODEL}.get(self.provider)
        return {"provider": self.provider, "model": model, "available": self.available()}

    def complete(self, system: str, user: str, max_tokens: int = 400,
                 temperature: float = 0.4) -> Optional[str]:
        if not self.available():
            return None
        try:
            if self.provider == "huggingface":
                return self._openai_chat(
                    "https://router.huggingface.co/v1/chat/completions",
                    settings.HF_API_TOKEN, settings.HF_MODEL, system, user,
                    max_tokens, temperature)
            if self.provider == "groq":
                return self._openai_chat(
                    "https://api.groq.com/openai/v1/chat/completions",
                    settings.GROQ_API_KEY, settings.GROQ_MODEL, system, user,
                    max_tokens, temperature)
            if self.provider == "ollama":
                return self._ollama(system, user, max_tokens, temperature)
        except Exception:
            return None
        return None

    # ------------------------------------------------------------------ #
    @staticmethod
    def _openai_chat(url, token, model, system, user, max_tokens, temperature) -> Optional[str]:
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": user}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()

    def _ollama(self, system, user, max_tokens, temperature) -> Optional[str]:
        r = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": settings.OLLAMA_MODEL,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": user}],
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()["message"]["content"].strip()


llm = LLMClient()
