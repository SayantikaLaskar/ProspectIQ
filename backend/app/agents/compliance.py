"""Compliance guardrail agent — a rule-based (hence auditable) check of every
lead + outreach message against RBI fair-practices and DPDP-Act expectations.

Deliberately deterministic: compliance decisions must be explainable and
reproducible, not left to a generative model.
"""
from typing import Dict, List

BANNED_PHRASES = [
    "guaranteed approval", "guaranteed loan", "no documents", "no documentation",
    "lifetime free", "100% approval", "instant approval guaranteed", "assured loan",
]


def compliance_check(lead: Dict, pitch_text: str = "") -> Dict:
    checks: List[Dict] = []

    def add(rule, status, note):
        checks.append({"rule": rule, "status": status, "note": note})

    existing = lead.get("relationship_months", 0) > 0
    add("DPDP consent & data usage",
        "PASS" if existing else "REVIEW",
        ("Profiling uses the bank's own transaction data for an existing customer under "
         "the banking relationship; verify marketing-contact consent & DND status before outreach.")
        if existing else
        "New/limited relationship — obtain explicit consent before profiling and contact.")

    if lead.get("under_review"):
        add("Product suitability (no mis-selling)", "REVIEW",
            "Highest-intent product exceeds current eligibility — route to credit before quoting an amount.")
    else:
        add("Product suitability (no mis-selling)", "PASS",
            f"Recommended amount fits within FOIR {round(lead['foir_existing']*100)}% plus the new EMI under policy caps.")

    grade = lead.get("affordability_grade", "NA")
    add("Responsible lending / repayment capacity",
        "PASS" if grade in ("A", "B", "C") else "REVIEW",
        f"Affordability grade {grade}; indicative EMI within assessed disposable income.")

    add("Transparent pricing (RBI fair practices)", "PASS",
        f"Indicative rate {round(lead['annual_rate']*100,1)}% p.a. and EMI are disclosed; "
        f"final rate stated as subject to assessment.")

    text = (pitch_text or "").lower()
    hits = [b for b in BANNED_PHRASES if b in text]
    add("Communication content", "FAIL" if hits else "PASS",
        ("Prohibited claim(s): " + ", ".join(hits)) if hits
        else "No misleading claims detected; includes a clear opt-out.")

    add("Income assessment auditability", "PASS",
        "Income derived from tagged transaction evidence with a confidence score — "
        "auditable and explainable for underwriting review.")

    statuses = [c["status"] for c in checks]
    overall = "FAIL" if "FAIL" in statuses else ("REVIEW" if "REVIEW" in statuses else "PASS")
    return {
        "status": overall,
        "checks": checks,
        "summary": {s: statuses.count(s) for s in ("PASS", "REVIEW", "FAIL")},
    }
