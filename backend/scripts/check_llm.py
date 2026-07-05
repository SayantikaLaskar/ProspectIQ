"""Check the configured LLM provider + probe live models (no secrets printed)."""
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.llm import LLMClient, llm
from app.config import settings

print("LLM_PROVIDER    :", settings.LLM_PROVIDER)
print("HF token set    :", bool(settings.HF_API_TOKEN), "(len", len(settings.HF_API_TOKEN), ")")
print("client.available:", llm.available())

if settings.LLM_PROVIDER == "huggingface" and settings.HF_API_TOKEN:
    candidates = [
        settings.HF_MODEL,
        "meta-llama/Llama-3.1-8B-Instruct",
        "Qwen/Qwen2.5-7B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.3",
        "HuggingFaceH4/zephyr-7b-beta",
        "google/gemma-2-9b-it",
    ]
    print("--- probing HF models your token can reach ---")
    seen = set()
    for mdl in candidates:
        if mdl in seen:
            continue
        seen.add(mdl)
        try:
            out = LLMClient._openai_chat(
                "https://router.huggingface.co/v1/chat/completions",
                settings.HF_API_TOKEN, mdl, "You are concise.", "Reply: HF OK", 16, 0.2)
            print(f"  [OK]   {mdl} -> {repr(out)[:90]}")
        except Exception as e:
            print(f"  [FAIL] {mdl} -> {str(e)[:110]}")
else:
    out = llm.complete("You are concise.", "Reply: HF OK", max_tokens=16)
    print("result:", repr(out)[:200] if out else "None (templates)")
