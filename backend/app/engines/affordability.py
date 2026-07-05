"""Repayment-capacity / affordability engine.

Turns the transaction stream into what an underwriter needs: existing
obligations, FOIR (Fixed-Obligation-to-Income Ratio), disposable income, and a
per-product eligible loan amount. This is the "quantifiable repayment capacity"
and "prudent underwriting" half of the brief.
"""
from typing import Dict, List

import numpy as np
import pandas as pd

from app.constants import PRODUCTS, emi, max_principal_for_emi

RECENT_MONTHS = 6
ESSENTIAL_CATS = {"rent", "utilities", "groceries", "insurance", "medical", "education"}


def _monthly_avg(df: pd.DataFrame, months_recent, cats=None) -> float:
    d = df[df["direction"] == "debit"]
    if cats is not None:
        d = d[d["category"].isin(cats)]
    d = d[d["month"].isin(months_recent)]
    if d.empty:
        return 0.0
    per_month = d.groupby("month")["amount"].sum().abs()
    return float(per_month.sum() / max(1, len(months_recent)))


def assess_affordability(profile: Dict, txns: pd.DataFrame, income: Dict) -> Dict:
    est_income = float(income.get("estimated_monthly_income", 0) or 0)
    result = {
        "estimated_monthly_income": round(est_income, 0),
        "existing_emi": 0.0, "credit_card_outflow": 0.0, "rent": 0.0,
        "essential_spend": 0.0, "monthly_obligations": 0.0,
        "disposable_income": 0.0, "savings_rate": 0.0, "foir_existing": 0.0,
        "balance_trend": "unknown", "grade": "NA",
        "eligibility": {}, "evidence": [],
    }
    if txns is None or txns.empty or est_income <= 0:
        result["evidence"] = ["Insufficient data to assess repayment capacity."]
        return result

    df = txns.copy()
    df["month"] = df["date"].dt.to_period("M")
    months = sorted(df["month"].unique())
    recent = months[-RECENT_MONTHS:] if len(months) >= RECENT_MONTHS else months

    existing_emi = _monthly_avg(df, recent, {"emi"})
    cc_outflow = _monthly_avg(df, recent, {"credit_card_payment"})
    rent = _monthly_avg(df, recent, {"rent"})
    essentials = _monthly_avg(df, recent, ESSENTIAL_CATS)
    total_outflow = _monthly_avg(df, recent, None)

    obligations = existing_emi + cc_outflow
    disposable = max(0.0, est_income - obligations - essentials)
    savings_rate = float((est_income - total_outflow) / est_income) if est_income else 0.0
    foir = float(obligations / est_income) if est_income else 0.0

    # balance trend (month-end balances)
    month_end = df.sort_values("date").groupby("month")["balance"].last()
    trend = "stable"
    if len(month_end) >= 3:
        slope = float(np.polyfit(range(len(month_end)), month_end.values, 1)[0])
        if slope > 0.05 * est_income:
            trend = "rising"
        elif slope < -0.05 * est_income:
            trend = "declining"

    # per-product eligibility via FOIR head-room
    eligibility: Dict[str, Dict] = {}
    for code, p in PRODUCTS.items():
        budget = max(0.0, est_income * p["max_foir"] - obligations)
        principal = max_principal_for_emi(budget, p["annual_rate"], p["tenure_months"])
        principal = min(principal, p["max_amount"])
        eligible = principal >= p["min_amount"] and budget > 0
        principal = principal if eligible else min(principal, p["min_amount"])
        indicative_emi = emi(principal, p["annual_rate"], p["tenure_months"]) if principal > 0 else 0.0
        eligibility[code] = {
            "eligible": bool(eligible),
            "eligible_amount": round(principal, -3),
            "indicative_emi": round(indicative_emi, 0),
            "new_emi_budget": round(budget, 0),
            "foir_with_new": round((obligations + indicative_emi) / est_income, 3) if est_income else 0.0,
        }

    # grade
    if foir < 0.2 and disposable > 0.35 * est_income:
        grade = "A"
    elif foir < 0.35 and disposable > 0.2 * est_income:
        grade = "B"
    elif foir < 0.5 and disposable > 0.1 * est_income:
        grade = "C"
    else:
        grade = "D"

    evidence: List[str] = []
    if existing_emi > 0:
        evidence.append(f"Existing EMI obligations of ₹{existing_emi:,.0f}/mo detected (FOIR {foir*100:.0f}%).")
    else:
        evidence.append("No existing loan EMIs detected — clean obligation profile.")
    evidence.append(f"Disposable income ≈ ₹{disposable:,.0f}/mo after obligations & essentials.")
    evidence.append(f"Month-end balance trend is {trend}; savings rate {savings_rate*100:.0f}%.")

    result.update({
        "existing_emi": round(existing_emi, 0),
        "credit_card_outflow": round(cc_outflow, 0),
        "rent": round(rent, 0),
        "essential_spend": round(essentials, 0),
        "monthly_obligations": round(obligations, 0),
        "disposable_income": round(disposable, 0),
        "savings_rate": round(savings_rate, 3),
        "foir_existing": round(foir, 3),
        "balance_trend": trend,
        "grade": grade,
        "eligibility": eligibility,
        "evidence": evidence,
    })
    return result
