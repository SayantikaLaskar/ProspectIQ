"""Income-estimation engine.

Recovers a customer's *actual* monthly income from their transaction stream --
the hard, high-value sub-problem the brief calls out ("accurate assessment of
borrowers' actual income levels"). Traditional metrics rely on declared income,
which the self-employed routinely understate.

Method (all from raw transactions, no ground-truth peeking):
  1. Detect a recurring salary credit (narration flag + monthly recurrence).
  2. Aggregate variable/business inflows (UPI collections, cash deposits),
     discounted for volatility so we don't over-credit lumpy months.
  3. Blend -> estimated income, classify salaried/self-employed/mixed, and
     attach a confidence score reflecting how verifiable the income is.
"""
from typing import Dict, List

import numpy as np
import pandas as pd

RECENT_MONTHS = 6


def _empty() -> Dict:
    return {
        "estimated_monthly_income": 0.0, "income_type": "unknown",
        "salary_component": 0.0, "variable_component": 0.0,
        "stability": 0.0, "confidence": 0.0, "months_observed": 0,
        "monthly_series": [], "evidence": ["No transaction history available."],
    }


def estimate_income(profile: Dict, txns: pd.DataFrame) -> Dict:
    if txns is None or txns.empty:
        return _empty()

    df = txns.copy()
    df["month"] = df["date"].dt.to_period("M")
    months = sorted(df["month"].unique())
    recent = months[-RECENT_MONTHS:] if len(months) >= RECENT_MONTHS else months

    credits = df[df["direction"] == "credit"].copy()
    if credits.empty:
        return _empty()
    narr = credits["narration"].str.upper()

    # ---- 1. recurring salary --------------------------------------------- #
    is_salary = narr.str.contains("SALARY", na=False)
    sal = credits[is_salary]
    salary_component, salary_months = 0.0, 0
    if not sal.empty:
        sal_recent = sal[sal["month"].isin(recent)]
        vals = sal_recent.sort_values("date")["amount"].tail(3)
        if not vals.empty:
            salary_component = float(vals.median())  # captures post-hike level
            salary_months = int(sal_recent["month"].nunique())

    # ---- 2. variable / business income ----------------------------------- #
    is_interest = narr.str.contains("INT.PD", na=False) | (credits["category"] == "interest")
    biz = credits[~is_salary & ~is_interest]
    biz_recent = biz[biz["month"].isin(recent)]
    variable_component, biz_cv, cash_share = 0.0, 0.0, 0.0
    if not biz_recent.empty:
        monthly_biz = biz_recent.groupby("month")["amount"].sum()
        med = float(monthly_biz.median())
        mean = float(monthly_biz.mean())
        biz_cv = float(monthly_biz.std() / mean) if mean > 0 and len(monthly_biz) > 1 else 0.0
        haircut = float(np.clip(1 - 0.35 * biz_cv, 0.55, 1.0))  # volatility discount
        variable_component = med * haircut
        cash = biz_recent[biz_recent["channel"] == "CASH"]["amount"].sum()
        cash_share = float(cash / biz_recent["amount"].sum()) if biz_recent["amount"].sum() > 0 else 0.0

    estimated = salary_component + variable_component
    if estimated <= 0:
        return _empty()

    # ---- 3. classify + score --------------------------------------------- #
    salary_share = salary_component / estimated
    if salary_component > 0 and variable_component > 0.25 * estimated:
        income_type = "mixed"
    elif salary_component >= variable_component:
        income_type = "salaried"
    else:
        income_type = "self_employed"

    # monthly total income series (salary + variable) for stability + charts
    inc_series = []
    monthly_totals = []
    for m in recent:
        m_sal = sal[sal["month"] == m]["amount"].sum() if not sal.empty else 0.0
        m_biz = biz[biz["month"] == m]["amount"].sum()
        total = float(m_sal + m_biz)
        monthly_totals.append(total)
        inc_series.append({"month": str(m), "income": round(total, 0)})
    mt = np.array([v for v in monthly_totals if v > 0], dtype=float)
    inc_cv = float(mt.std() / mt.mean()) if mt.size > 1 and mt.mean() > 0 else 0.0
    stability = float(np.clip(1 - inc_cv, 0.0, 1.0))

    digital_share = 1.0 - cash_share
    confidence = float(np.clip(
        0.35 + 0.45 * salary_share + 0.20 * digital_share - 0.20 * cash_share, 0.2, 0.98))

    declared = float(profile.get("declared_monthly_income", 0) or 0)
    uplift_pct = round((estimated / declared - 1) * 100, 1) if declared > 0 else 0.0

    evidence: List[str] = []
    if salary_component > 0:
        evidence.append(
            f"Recurring salary credit of ₹{salary_component:,.0f} detected in "
            f"{salary_months}/{len(recent)} recent months.")
    if variable_component > 0:
        evidence.append(
            f"Variable inflows average ₹{variable_component:,.0f}/mo "
            f"(volatility {biz_cv*100:.0f}%, cash share {cash_share*100:.0f}%).")
    if declared > 0:
        verb = "above" if uplift_pct >= 0 else "below"
        evidence.append(
            f"Estimated income is {abs(uplift_pct):.0f}% {verb} the declared "
            f"₹{declared:,.0f}/mo.")

    return {
        "estimated_monthly_income": round(estimated, 0),
        "income_type": income_type,
        "salary_component": round(salary_component, 0),
        "variable_component": round(variable_component, 0),
        "stability": round(stability, 3),
        "confidence": round(confidence, 3),
        "months_observed": len(months),
        "declared_monthly_income": round(declared, 0),
        "income_uplift_pct": uplift_pct,
        "monthly_series": inc_series,
        "evidence": evidence,
    }
