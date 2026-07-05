"""Agentic orchestrator — runs the per-lead agent pipeline and powers the RM
chat copilot. Works fully offline (templates); richer with an LLM configured.
"""
from typing import Dict, List, Optional

from app.agents import compliance as comp_agent
from app.agents import objections as obj_agent
from app.agents import prospect_analyst
from app.agents import pitch as pitch_agent
from app.agents import underwriting as uw_agent
from app.agents.common import PRODUCT_HUMAN, facts, inr, lakh
from app.agents.llm import llm

CHAT_SYSTEM = (
    "You are Prospect IQ, an AI copilot for an IDBI Bank relationship manager. "
    "Answer the RM's question about THIS prospect concisely and factually, using "
    "ONLY the facts provided. Be practical, compliant, and never invent numbers. "
    "Plain text."
)


def run_all(lead: Dict, channel: str = "WHATSAPP") -> Dict:
    analyst = prospect_analyst.analyze(lead)
    pitch = pitch_agent.generate_pitch(lead, channel)
    objections = obj_agent.objection_prep(lead)
    compliance = comp_agent.compliance_check(lead, pitch.get("message", ""))
    underwriting = uw_agent.underwriting_brief(lead)
    return {
        "customer_id": lead["customer_id"],
        "analyst": analyst,
        "pitch": pitch,
        "objections": objections,
        "compliance": compliance,
        "underwriting": underwriting,
        "llm": llm.info(),
    }


def chat(lead: Dict, question: str, history: Optional[List[Dict]] = None) -> Dict:
    if llm.available():
        convo = ""
        for h in (history or [])[-6:]:
            convo += f"{h.get('role', 'user')}: {h.get('content', '')}\n"
        user = (f"Prospect facts (JSON):\n{facts(lead)}\n\nConversation so far:\n{convo}\n"
                f"RM question: {question}\n\nAnswer:")
        text = llm.complete(CHAT_SYSTEM, user, max_tokens=300, temperature=0.4)
        if text:
            return {"answer": text, "grounded": True, "generated_by": llm.info()}
    return {"answer": _template_answer(lead, question), "grounded": True, "generated_by": llm.info()}


def _template_answer(lead: Dict, question: str) -> str:
    q = (question or "").lower()
    prod = PRODUCT_HUMAN.get(lead["recommended_product"], lead["recommended_product"])
    why = (lead.get("why_now") or {}).get("description")
    if any(k in q for k in ["income", "earn", "salary"]):
        return (f"Transaction-verified income is {inr(lead['estimated_monthly_income'])}/mo "
                f"(declared {inr(lead['declared_monthly_income'])}/mo, confidence "
                f"{round(lead['income_confidence']*100)}%, type {lead['income_type'].replace('_',' ')}).")
    if any(k in q for k in ["why", "product", "recommend", "offer", "best"]):
        base = (f"Best-fit is {prod} (intent {round(lead['top_intent_score'])}/100), eligible up to "
                f"{lakh(lead['recommended_amount'])} at ~{round(lead['annual_rate']*100,1)}% "
                f"({inr(lead['indicative_emi'])}/mo).")
        return base + (f" Why now: {why}" if why else "")
    if any(k in q for k in ["eligib", "amount", "how much", "qualify"]):
        return (f"Assessed eligibility is up to {lakh(lead['recommended_amount'])} for a {prod} "
                f"(EMI ~{inr(lead['indicative_emi'])}/mo, FOIR {round(lead['foir_existing']*100)}%, "
                f"affordability grade {lead['affordability_grade']}).")
    if any(k in q for k in ["risk", "default", "concern", "red flag"]):
        return (f"Credit score {lead['credit_score']}, affordability grade {lead['affordability_grade']}, "
                f"existing FOIR {round(lead['foir_existing']*100)}%, income confidence "
                f"{round(lead['income_confidence']*100)}%. See the underwriting brief for detailed flags.")
    if any(k in q for k in ["convert", "likely", "chance", "probab"]):
        return f"Predicted conversion for {lead['name']} is {round(lead['predicted_conversion']*100)}% ({lead['band']} band)."
    if any(k in q for k in ["contact", "pitch", "call", "message", "approach", "when"]):
        return (f"Lead with the trigger — {why or 'their strong banking relationship'} — and offer the "
                f"pre-qualified {prod}. Use the generated pitch and objection prep in this panel.")
    return (f"{lead['name']} — {prod} prospect, {round(lead['predicted_conversion']*100)}% predicted "
            f"conversion, verified income {inr(lead['estimated_monthly_income'])}/mo, eligible up to "
            f"{lakh(lead['recommended_amount'])}. Ask me about income, eligibility, risk, why-now, or approach.")
