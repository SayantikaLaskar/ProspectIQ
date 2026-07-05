"""Intent / propensity engine + "why-now" trigger detection.

Reads behavioural fingerprints from the transaction stream to score, per loan
product, how likely the customer is to *want* it right now — the "genuinely
interested prospects using transaction and behavioral insights" requirement.
"""
import math
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from app.constants import PRODUCT_ORDER

RECENT = 3


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _monthly_sum(df: pd.DataFrame, cats) -> pd.Series:
    d = df[df["category"].isin(cats)] if isinstance(cats, (set, list)) else df[df["category"] == cats]
    if d.empty:
        return pd.Series(dtype=float)
    return d.groupby("month")["amount"].sum().abs()


def detect_intent(profile: Dict, txns: pd.DataFrame, income: Dict) -> Dict:
    empty = {"product_scores": {p: 0 for p in PRODUCT_ORDER}, "top_product": None,
             "top_score": 0, "why_now": None, "signals": {}, "evidence": []}
    if txns is None or txns.empty:
        return empty

    df = txns.copy()
    df["month"] = df["date"].dt.to_period("M")
    months = sorted(df["month"].unique())
    if not months:
        return empty
    recent_m = months[-RECENT:]
    earlier_m = months[:-RECENT] if len(months) > RECENT else months
    narr = df["narration"].str.upper()
    est_income = float(income.get("estimated_monthly_income", 0) or 1)
    stability = float(income.get("stability", 0))
    age = int(profile.get("age", 35))

    def recent_mean(cats):
        s = _monthly_sum(df[df["month"].isin(recent_m)], cats)
        return float(s.sum() / max(1, len(recent_m)))

    def earlier_mean(cats):
        s = _monthly_sum(df[df["month"].isin(earlier_m)], cats)
        return float(s.sum() / max(1, len(earlier_m)))

    # ---- raw behavioural signals ---- #
    rent_recent = recent_mean({"rent"})
    is_renter = rent_recent > 0
    sip_series = _monthly_sum(df, {"sip"})
    sip_rising = len(sip_series) >= 3 and float(sip_series.iloc[-1]) > float(sip_series.iloc[0]) * 1.15
    fuel_recent, fuel_earlier = recent_mean({"fuel"}), earlier_mean({"fuel"})
    fuel_rising = fuel_recent > fuel_earlier * 1.25 and fuel_recent > 0
    auto_booking = bool(narr[df["month"].isin(recent_m)].str.contains("BOOKING TOKEN|AUTOMALL|SHOWROOM|DEALER", na=False).any())
    big_expense = df[df["month"].isin(recent_m) & df["category"].isin({"medical", "education", "travel"})]
    big_expense_recent = bool((big_expense["amount"].abs() > 0.5 * est_income).any())
    cc_recent = recent_mean({"credit_card_payment"})
    high_cc = cc_recent > 0.15 * est_income
    property_owner = bool(narr.str.contains("PROPERTY TAX", na=False).any())
    supplier_recent = bool(df[df["month"].isin(recent_m)]["narration"].str.upper().str.contains("SUPPLIER", na=False).any())
    biz_recent, biz_earlier = recent_mean({"business_income", "cash_deposit"}), earlier_mean({"business_income", "cash_deposit"})
    biz_growth = biz_recent > biz_earlier * 1.2 and biz_recent > 0

    # balance depletion (liquidity tightening)
    month_end = df.sort_values("date").groupby("month")["balance"].last()
    liquidity_tightening = False
    if len(month_end) >= 3:
        slope = float(np.polyfit(range(len(month_end)), month_end.values, 1)[0])
        liquidity_tightening = slope < -0.03 * est_income and float(month_end.iloc[-1]) < 0.5 * est_income

    signals = {
        "is_renter": is_renter, "sip_rising": sip_rising, "fuel_rising": fuel_rising,
        "auto_booking": auto_booking, "big_expense_recent": big_expense_recent,
        "high_cc_utilization": high_cc, "property_owner": property_owner,
        "business_growth": biz_growth or supplier_recent, "liquidity_tightening": liquidity_tightening,
    }

    # ---- per-product propensity ---- #
    home = -1.4 + 2.4 * is_renter + 1.8 * sip_rising + 0.5 * (27 <= age <= 45) + 0.4 * (stability > 0.7)
    auto = -1.4 + 3.0 * auto_booking + 2.0 * fuel_rising + 0.5 * (25 <= age <= 52)
    personal = -1.4 + 2.4 * big_expense_recent + 1.8 * liquidity_tightening + 1.1 * high_cc
    mortgage = -1.8 + 2.0 * property_owner + 1.8 * (biz_growth or supplier_recent) + 0.8 * (profile.get("employment_type") != "salaried")
    scores = {
        "HOME_LOAN": round(_sigmoid(home) * 100, 1),
        "AUTO_LOAN": round(_sigmoid(auto) * 100, 1),
        "PERSONAL_LOAN": round(_sigmoid(personal) * 100, 1),
        "MORTGAGE_LOAN": round(_sigmoid(mortgage) * 100, 1),
    }
    top_product = max(scores, key=scores.get)
    top_score = scores[top_product]

    # ---- "why now" trigger ---- #
    why_now = _detect_trigger(df, months, recent_m, earlier_m, signals, top_product)

    evidence = _evidence_for(top_product, signals, rent_recent, fuel_recent, fuel_earlier)
    return {"product_scores": scores, "top_product": top_product, "top_score": top_score,
            "why_now": why_now, "signals": signals, "evidence": evidence}


def _detect_trigger(df, months, recent_m, earlier_m, signals, top_product) -> Optional[Dict]:
    narr = df["narration"].str.upper()
    # salary hike
    sal = df[narr.str.contains("SALARY", na=False)].sort_values("date")
    if len(sal) >= 4:
        first_half = sal["amount"].head(2).median()
        last_half = sal["amount"].tail(2).median()
        if last_half > first_half * 1.15:
            return {"trigger": "salary_hike",
                    "description": f"Salary rose ~{(last_half/first_half-1)*100:.0f}% recently — higher repayment capacity unlocked.",
                    "recency_months": 1}
    # EMI closure
    emi_series = _monthly_sum(df, {"emi"})
    if len(emi_series) >= 4:
        recent_emi = emi_series[[m for m in emi_series.index if m in recent_m]].sum()
        earlier_emi = emi_series[[m for m in emi_series.index if m in earlier_m]].sum()
        if earlier_emi > 0 and recent_emi == 0:
            return {"trigger": "emi_closure",
                    "description": "An existing EMI recently closed — freed-up monthly capacity, prime for a new loan.",
                    "recency_months": 2}
    if signals["auto_booking"]:
        return {"trigger": "dealer_enquiry",
                "description": "Recent payment to a car dealer/showroom — active in-market auto buyer.",
                "recency_months": 1}
    if signals["big_expense_recent"]:
        return {"trigger": "large_expense",
                "description": "Large medical/education/travel outflow recently — likely needs short-term financing.",
                "recency_months": 1}
    if signals["business_growth"]:
        return {"trigger": "business_expansion",
                "description": "Business inflows and supplier payments rising — working-capital / LAP need.",
                "recency_months": 2}
    if signals["is_renter"] and signals["sip_rising"]:
        return {"trigger": "down_payment_building",
                "description": "Renter steadily growing investments — accumulating a home down-payment.",
                "recency_months": 3}
    return None


def _evidence_for(product, signals, rent_recent, fuel_recent, fuel_earlier) -> List[str]:
    ev: List[str] = []
    if product == "HOME_LOAN":
        if signals["is_renter"]:
            ev.append(f"Pays monthly rent (₹{rent_recent:,.0f}) — a renter, prime home-loan candidate.")
        if signals["sip_rising"]:
            ev.append("Investments/SIP rising steadily — building a down-payment corpus.")
    elif product == "AUTO_LOAN":
        if signals["auto_booking"]:
            ev.append("Recent car-dealer/showroom payment detected — active auto shopper.")
        if signals["fuel_rising"]:
            ev.append(f"Fuel spend up (₹{fuel_earlier:,.0f}→₹{fuel_recent:,.0f}/mo) — rising vehicle usage.")
    elif product == "PERSONAL_LOAN":
        if signals["big_expense_recent"]:
            ev.append("Large recent lifestyle/medical/education outflow — financing need.")
        if signals["liquidity_tightening"]:
            ev.append("Month-end balances declining — short-term liquidity gap.")
        if signals["high_cc_utilization"]:
            ev.append("High credit-card outflow — candidate for lower-rate consolidation.")
    elif product == "MORTGAGE_LOAN":
        if signals["property_owner"]:
            ev.append("Property-tax payments detected — owns property (collateral available).")
        if signals["business_growth"]:
            ev.append("Business inflows & supplier payments rising — working-capital need.")
    if not ev:
        ev.append("Behavioural signals are mild; monitor for stronger buying intent.")
    return ev
