"""Small helpers shared by the agents (Indian number formatting, labels)."""
import json
from typing import Dict

PRODUCT_HUMAN = {
    "PERSONAL_LOAN": "Personal Loan",
    "HOME_LOAN": "Home Loan",
    "AUTO_LOAN": "Auto Loan",
    "MORTGAGE_LOAN": "Loan Against Property",
}


def inr(n) -> str:
    """Format a number with Indian digit grouping, e.g. 1234567 -> ₹12,34,567."""
    try:
        n = int(round(float(n or 0)))
    except (TypeError, ValueError):
        n = 0
    neg = n < 0
    s = str(abs(n))
    if len(s) > 3:
        last3, rest, parts = s[-3:], s[:-3], []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        s = ",".join(parts) + "," + last3
    return ("-" if neg else "") + "₹" + s


def lakh(n) -> str:
    """Compact rupees, e.g. 1200000 -> ₹12.0 L, 15000000 -> ₹1.50 Cr."""
    n = float(n or 0)
    if abs(n) >= 1e7:
        return f"₹{n / 1e7:.2f} Cr"
    if abs(n) >= 1e5:
        return f"₹{n / 1e5:.1f} L"
    return inr(n)


def facts(lead: Dict) -> str:
    """Compact JSON of a lead's key facts — used to ground the LLM prompts so
    agents never hallucinate numbers."""
    why = lead.get("why_now") or {}
    return json.dumps({
        "name": lead["name"], "age": lead["age"], "city": lead["city"],
        "employment": lead["employment_type"],
        "declared_income_monthly": lead["declared_monthly_income"],
        "verified_income_monthly": lead["estimated_monthly_income"],
        "income_uplift_pct": lead.get("income_uplift_pct", 0),
        "income_confidence_pct": round(lead["income_confidence"] * 100),
        "credit_score": lead["credit_score"],
        "relationship_months": lead["relationship_months"],
        "existing_products": lead["existing_products"],
        "recommended_product": PRODUCT_HUMAN.get(lead["recommended_product"], lead["recommended_product"]),
        "intent_score": round(lead["top_intent_score"]),
        "why_now": why.get("description"),
        "eligible_amount": lead["recommended_amount"],
        "indicative_emi": lead["indicative_emi"],
        "interest_rate_pct": round(lead["annual_rate"] * 100, 1),
        "foir_pct": round(lead["foir_existing"] * 100),
        "affordability_grade": lead["affordability_grade"],
        "predicted_conversion_pct": round(lead["predicted_conversion"] * 100),
    }, ensure_ascii=False)

