"""Prospect Analyst agent — a plain-English brief explaining *why* this lead
scores the way it does. Deterministic template, optionally polished by an LLM.
"""
from typing import Dict

from app.agents.common import PRODUCT_HUMAN, facts, inr, lakh
from app.agents.llm import llm

SYSTEM = (
    "You are a senior relationship analyst at IDBI Bank. In 3-4 crisp, factual "
    "sentences write a prospect brief for a relationship manager. Use ONLY the "
    "facts provided; never invent numbers. Indian retail-banking context. "
    "Plain text, no markdown, no preamble."
)


def _template(lead: Dict) -> str:
    emp = lead["employment_type"].replace("_", "-")
    prod = PRODUCT_HUMAN.get(lead["recommended_product"], lead["recommended_product"])
    est, decl = lead["estimated_monthly_income"], lead["declared_monthly_income"]
    uplift = lead.get("income_uplift_pct", 0)
    why = lead.get("why_now") or {}
    conv = round(lead["predicted_conversion"] * 100)
    p = [f"{lead['name']} is a {lead['age']}-year-old {emp} customer in {lead['city']} "
         f"(relationship {lead['relationship_months']} months, CIBIL {lead['credit_score']})."]
    if abs(uplift) >= 5:
        p.append(f"Transaction-verified income is {inr(est)}/mo — {abs(uplift):.0f}% "
                 f"{'above' if uplift >= 0 else 'below'} the declared {inr(decl)}/mo.")
    else:
        p.append(f"Transaction-verified income is {inr(est)}/mo "
                 f"(confidence {round(lead['income_confidence']*100)}%).")
    p.append(f"Strongest intent is {prod} (intent {round(lead['top_intent_score'])}/100)"
             + (f"; {why.get('description').rstrip('.')}" if why else "") + ".")
    p.append(f"Grade {lead['affordability_grade']} on affordability "
             f"(FOIR {round(lead['foir_existing']*100)}%); eligible up to {lakh(lead['recommended_amount'])} "
             f"at ~{round(lead['annual_rate']*100,1)}% ({inr(lead['indicative_emi'])}/mo). "
             f"Predicted conversion {conv}%.")
    return " ".join(p)


def analyze(lead: Dict) -> Dict:
    prod = PRODUCT_HUMAN.get(lead["recommended_product"], lead["recommended_product"])
    conv = round(lead["predicted_conversion"] * 100)
    summary = _template(lead)
    text = llm.complete(SYSTEM, "Prospect facts (JSON):\n" + facts(lead) + "\n\nWrite the brief.",
                        max_tokens=260, temperature=0.3)
    if text:
        summary = text
    key_points = [
        f"Verified income {inr(lead['estimated_monthly_income'])}/mo"
        + (f" ({lead['income_uplift_pct']:+.0f}% vs declared)" if abs(lead.get("income_uplift_pct", 0)) >= 5 else ""),
        f"Best-fit: {prod} up to {lakh(lead['recommended_amount'])} ({inr(lead['indicative_emi'])}/mo)",
        f"Affordability grade {lead['affordability_grade']}, FOIR {round(lead['foir_existing']*100)}%",
    ]
    why = lead.get("why_now") or {}
    if why:
        key_points.insert(1, f"Why now: {why.get('trigger','').replace('_',' ').title()}")
    return {
        "summary": summary,
        "headline": f"{prod} — {conv}% likely · {lakh(lead['recommended_amount'])} opportunity",
        "key_points": key_points,
        "generated_by": llm.info(),
    }
