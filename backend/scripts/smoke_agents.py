"""Exercise the agentic pipeline (template mode) on the top-ranked lead."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json

from app.data.store import store
from app.leads import lead_service
from app.agents import orchestrator

store.ensure_loaded()
lead_service.build()
lead = lead_service.get_lead(lead_service.leads[0]["customer_id"])
print("TOP LEAD:", lead["name"], "|", lead["recommended_product_label"],
      "|", round(lead["predicted_conversion"] * 100), "% likely\n")

out = orchestrator.run_all(lead, channel="WHATSAPP")
print("--- ANALYST ---\n", out["analyst"]["summary"], "\n")
print("--- PITCH (WhatsApp) ---\n", out["pitch"]["message"], "\n")
print("--- OBJECTIONS ---")
for o in out["objections"]["objections"]:
    print(" Q:", o["objection"], "\n A:", o["response"])
print("\n--- COMPLIANCE:", out["compliance"]["status"], "---")
for c in out["compliance"]["checks"]:
    print(f"  [{c['status']}] {c['rule']}")
print("\n--- UNDERWRITING:", out["underwriting"]["recommendation"], "---")
print(" ", out["underwriting"]["opinion"])
print(" risk_flags:", out["underwriting"]["risk_flags"])
print("\n--- CHAT ---")
for q in ["What's their real income?", "Why this product?", "Any risks?"]:
    print(" RM:", q, "\n IQ:", orchestrator.chat(lead, q)["answer"])
print("\nLLM provider:", out["llm"])
