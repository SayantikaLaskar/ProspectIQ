"""Underwriting-brief agent — turns the engine outputs into a structured
pre-underwriting note the credit team can act on ("prudent underwriting").
"""
from typing import Dict, List

from app.agents.common import PRODUCT_HUMAN, facts, inr, lakh
from app.agents.llm import llm

SYSTEM = (
    "You are a credit underwriter at IDBI Bank. In 2-3 sentences give a concise "
    "pre-underwriting opinion using ONLY the facts. Reference the income basis, "
    "FOIR and any key risk. Plain text, no markdown."
)


def _recommendation(lead: Dict) -> str:
    if lead.get("under_review"):
        return "REFER TO CREDIT"
    grade, score = lead["affordability_grade"], lead["credit_score"]
    if grade in ("A", "B") and score >= 680:
        return "PROCEED"
    if grade in ("A", "B", "C") and score >= 650:
        return "PROCEED WITH CONDITIONS"
    return "REFER TO CREDIT"


def _opinion(lead: Dict, rec: str) -> str:
    inc = lead["income"]
    prod = PRODUCT_HUMAN.get(lead["recommended_product"], lead["recommended_product"])
    basis = {"salaried": "verified recurring salary credits",
             "self_employed": "banking-surrogate business inflows",
             "mixed": "salary plus business inflows"}.get(inc["income_type"], "transaction inflows")
    return (f"Income of {inr(inc['estimated_monthly_income'])}/mo established from {basis} "
            f"(confidence {round(inc['confidence']*100)}%). With existing FOIR "
            f"{round(lead['foir_existing']*100)}%, a {prod} of {lakh(lead['recommended_amount'])} "
            f"(EMI {inr(lead['indicative_emi'])}/mo) is supported. Recommendation: {rec}.")


def underwriting_brief(lead: Dict) -> Dict:
    inc, aff = lead["income"], lead["affordability"]
    code = lead["recommended_product"]
    elig = aff.get("eligibility", {}).get(code, {})

    flags: List[str] = []
    if inc.get("confidence", 0) < 0.5:
        flags.append("Income confidence moderate/low (variable or cash-heavy inflows) — seek supporting proof.")
    if inc.get("income_type") == "self_employed":
        flags.append("Self-employed — income volatility; corroborate with GST/ITR.")
    if aff.get("foir_existing", 0) > 0.4:
        flags.append(f"Existing FOIR elevated ({round(aff['foir_existing']*100)}%).")
    if aff.get("balance_trend") == "declining":
        flags.append("Month-end balances declining — monitor liquidity.")
    if lead.get("credit_score", 700) < 680:
        flags.append(f"CIBIL {lead['credit_score']} below prime threshold.")
    if not flags:
        flags.append("No material risk flags from transaction analysis.")

    rec = _recommendation(lead)
    assessment = {
        "verified_monthly_income": inc["estimated_monthly_income"],
        "income_type": inc["income_type"],
        "income_confidence": inc["confidence"],
        "declared_monthly_income": lead["declared_monthly_income"],
        "existing_obligations": aff["monthly_obligations"],
        "foir_existing": aff["foir_existing"],
        "disposable_income": aff["disposable_income"],
        "recommended_product": PRODUCT_HUMAN.get(code, code),
        "recommended_exposure": lead["recommended_amount"],
        "indicative_emi": lead["indicative_emi"],
        "foir_with_new": elig.get("foir_with_new"),
        "credit_score": lead["credit_score"],
    }
    opinion = _opinion(lead, rec)
    llm_text = llm.complete(
        SYSTEM, "Facts (JSON):\n" + facts(lead) + f"\nRisk flags: {flags}",
        max_tokens=200, temperature=0.2)
    if llm_text:
        opinion = llm_text
    return {
        "assessment": assessment,
        "risk_flags": flags,
        "evidence": (inc.get("evidence", []) + aff.get("evidence", []))[:6],
        "recommendation": rec,
        "opinion": opinion,
        "generated_by": llm.info(),
    }
