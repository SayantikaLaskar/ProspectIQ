"""Outreach agent — a personalised, compliant pitch for a chosen channel,
woven around the customer's "why-now" trigger. Template-first, LLM-polished.
"""
from typing import Dict

from app.agents.common import PRODUCT_HUMAN, facts, inr, lakh
from app.agents.llm import llm

CHANNELS = ["WHATSAPP", "SMS", "EMAIL", "CALL_SCRIPT"]

SYSTEM = (
    "You are an outreach copywriter for IDBI Bank's retail-lending team. Write a "
    "warm, concise, personalised message for the given channel. Rules: use ONLY "
    "the facts given; NEVER promise 'guaranteed approval', 'no documents', or "
    "unrealistic claims; always keep it RBI fair-practices compliant and include "
    "a soft opt-out. Indian context. Return only the message text."
)


def _template(lead: Dict, channel: str) -> Dict:
    first = lead["name"].split()[0]
    prod = PRODUCT_HUMAN.get(lead["recommended_product"], lead["recommended_product"])
    amt, emi = lakh(lead["recommended_amount"]), inr(lead["indicative_emi"])
    rate = round(lead["annual_rate"] * 100, 1)
    why = (lead.get("why_now") or {}).get("description", "")
    hook = f" We noticed {why[0].lower() + why[1:]}" if why else ""
    out = {"channel": channel, "subject": None}
    if channel == "SMS":
        out["message"] = (
            f"Dear {first}, as a valued IDBI Bank customer you are pre-qualified for a "
            f"{prod} up to {amt} at {rate}% p.a. (EMI ~{emi}/mo). Reply YES for details "
            f"or STOP to opt out. -IDBI Bank")
    elif channel == "WHATSAPP":
        out["message"] = (
            f"Hi {first}! 👋\n\nBased on your IDBI Bank relationship, you're *pre-qualified* "
            f"for a *{prod}* up to *{amt}* at an attractive *{rate}% p.a.* "
            f"(indicative EMI ~{emi}/month).{hook}\n\n"
            f"Shall I share the details and a quick, paperless application link? "
            f"Reply *STOP* to opt out anytime.")
    elif channel == "EMAIL":
        out["subject"] = f"{first}, your pre-qualified {prod} offer from IDBI Bank"
        out["message"] = (
            f"Dear {first},\n\nThank you for banking with IDBI Bank. Based on your "
            f"relationship with us, you are pre-qualified for a {prod} of up to {amt} "
            f"at an indicative rate of {rate}% p.a. (EMI approx. {emi}/month).{hook}\n\n"
            f"Our relationship team can walk you through eligibility and a quick, "
            f"minimal-documentation process at your convenience.\n\n"
            f"Warm regards,\nIDBI Bank Retail Lending\n\n"
            f"To unsubscribe from such offers, reply UNSUBSCRIBE.")
    else:  # CALL_SCRIPT
        out["message"] = (
            f"• Open: Greet {first}, thank them for banking with IDBI.\n"
            f"• Context: Reference the trigger — {why or 'their strong banking relationship'}.\n"
            f"• Offer: Pre-qualified {prod} up to {amt} at ~{rate}% p.a., EMI ~{emi}/mo.\n"
            f"• Value: Relationship pricing, minimal documentation, quick disbursal.\n"
            f"• Close: Offer to email details / book a branch or video appointment.\n"
            f"• Compliance: Confirm consent to be contacted; note interest is indicative, "
            f"subject to final assessment.")
    return out


def generate_pitch(lead: Dict, channel: str = "WHATSAPP") -> Dict:
    channel = channel.upper()
    if channel not in CHANNELS:
        channel = "WHATSAPP"
    out = _template(lead, channel)
    user = (f"Channel: {channel}\nProspect facts (JSON):\n{facts(lead)}\n\n"
            f"Write the {channel.lower()} message.")
    text = llm.complete(SYSTEM, user, max_tokens=320, temperature=0.6)
    if text:
        out["message"] = text
    out["generated_by"] = llm.info()
    return out
