"""Objection-handling agent — anticipates likely push-backs and arms the RM
with grounded, compliant responses tailored to this prospect.
"""
from typing import Dict, List

from app.agents.common import PRODUCT_HUMAN, inr, lakh


def objection_prep(lead: Dict) -> Dict:
    prod = PRODUCT_HUMAN.get(lead["recommended_product"], lead["recommended_product"])
    rate = round(lead["annual_rate"] * 100, 1)
    why = lead.get("why_now") or {}
    items: List[Dict] = [{
        "objection": "The interest rate seems high.",
        "response": (f"As an existing IDBI customer you qualify for relationship pricing "
                     f"at ~{rate}% p.a.; we can also tune the tenure to keep the EMI "
                     f"comfortable at ~{inr(lead['indicative_emi'])}/month."),
    }]
    if why:
        items.append({
            "objection": "I'm not looking for a loan right now.",
            "response": (f"Understood — I reached out because {why.get('description','').rstrip('.')}. "
                         f"The pre-approval carries no obligation, so you can simply keep it ready."),
        })
    else:
        items.append({
            "objection": "I'm not looking for a loan right now.",
            "response": ("No problem — this is a pre-approved offer with no obligation; "
                         "I can keep it on file so funds are ready whenever you need them."),
        })
    if lead.get("foir_existing", 0) > 0.05 or "Credit Card" in lead.get("existing_products", []):
        items.append({
            "objection": "I already have EMIs / borrow elsewhere.",
            "response": (f"We can explore a balance-transfer or top-up — your assessed capacity "
                         f"supports up to {lakh(lead['recommended_amount'])}, which can lower "
                         f"your overall monthly outflow."),
        })
    items.append({
        "objection": "There's too much paperwork.",
        "response": ("Because you already bank with us, the application is largely pre-filled "
                     "with minimal documentation and a digital process — much of the assessment "
                     "is already done from your relationship."),
    })
    return {"objections": items[:4]}
