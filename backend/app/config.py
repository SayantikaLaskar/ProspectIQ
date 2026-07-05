"""Central configuration for the Prospect IQ backend.

Everything has a safe default so the whole system runs end-to-end with no
API keys and no external services. Override via a `.env` file in `backend/`.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # .../backend
load_dotenv(BASE_DIR / ".env")


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


class Settings:
    # --- Agentic LLM layer ---
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "template").strip().lower()
    HF_API_TOKEN = os.getenv("HF_API_TOKEN", "").strip()
    HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct").strip()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1").strip()

    # --- Synthetic data ---
    NUM_CUSTOMERS = _int("NUM_CUSTOMERS", 2500)
    RANDOM_SEED = _int("RANDOM_SEED", 42)
    DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data_store")

    # --- API ---
    CORS_ORIGINS = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
        ).split(",")
        if o.strip()
    ]


settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
