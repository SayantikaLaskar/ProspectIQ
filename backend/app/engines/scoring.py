"""Fusion layer: turn the three engine outputs into a ranked, explainable lead.

- recommend_product : highest-intent product the customer is *eligible* for.
- build_features    : rich numeric vector for the ML conversion model (cashflow
                      health + per-product intent + individual behavioural signals).
- lead_quality_score: transparent 0-100 blend (Intent / Income / Affordability /
                      Profile) so an RM or auditor can see *why* a lead scores.
"""
from typing import Dict

import numpy as np

from app.constants import PRODUCTS

FEATURE_NAMES = [
    "est_income", "income_confidence", "income_stability", "disposable_income",
    "foir_existing", "savings_rate", "balance_trend", "top_intent", "top2_gap",
    "signal_count", "has_trigger", "credit_score", "relationship_months",
    "num_products", "eligible_top", "headroom_ratio",
    "intent_home", "intent_auto", "intent_personal", "intent_mortgage",
    "sig_renter", "sig_sip_rising", "sig_auto_booking", "sig_big_expense",
    "sig_high_cc", "sig_business_growth", "sig_liquidity_tightening",
]
GRADE_PTS = {"A": 25, "B": 19, "C": 12, "D": 5, "NA": 5}
TREND_NUM = {"rising": 1.0, "stable": 0.0, "declining": -1.0, "unknown": 0.0}


def recommend_product(intent: Dict, afford: Dict) -> Dict:
    scores = intent.get("product_scores", {}) or {}
    elig = afford.get("eligibility", {}) or {}
    ranked = sorted(scores, key=lambda k: scores[k], reverse=True) or list(PRODUCTS)
    chosen, under_review = None, False
    for code in ranked:
        if elig.get(code, {}).get("eligible"):
            chosen = code
            break
    if chosen is None:  # wants something but doesn't yet qualify -> flag for review
        chosen = ranked[0]
        under_review = True
    e = elig.get(chosen, {})
    p = PRODUCTS[chosen]
    return {
        "product": chosen, "label": p["label"], "annual_rate": p["annual_rate"],
        "tenure_months": p["tenure_months"],
        "recommended_amount": e.get("eligible_amount", 0),
        "indicative_emi": e.get("indicative_emi", 0),
        "intent_score": scores.get(chosen, 0),
        "eligible": not under_review, "under_review": under_review,
    }


def build_features(profile: Dict, income: Dict, afford: Dict, intent: Dict, reco: Dict) -> Dict:
    est = float(income.get("estimated_monthly_income", 0) or 0)
    headroom = float(afford.get("eligibility", {}).get(reco["product"], {}).get("new_emi_budget", 0))
    ps = intent.get("product_scores", {}) or {}
    ordered = sorted(ps.values(), reverse=True) or [0.0, 0.0]
    top2_gap = (ordered[0] - (ordered[1] if len(ordered) > 1 else 0.0)) / 100.0
    sig = intent.get("signals", {}) or {}
    return {
        "est_income": est,
        "income_confidence": float(income.get("confidence", 0)),
        "income_stability": float(income.get("stability", 0)),
        "disposable_income": float(afford.get("disposable_income", 0)),
        "foir_existing": float(afford.get("foir_existing", 0)),
        "savings_rate": float(afford.get("savings_rate", 0)),
        "balance_trend": TREND_NUM.get(afford.get("balance_trend", "unknown"), 0.0),
        "top_intent": float(intent.get("top_score", 0)) / 100.0,
        "top2_gap": top2_gap,
        "signal_count": float(sum(1 for v in sig.values() if v)),
        "has_trigger": 1.0 if intent.get("why_now") else 0.0,
        "credit_score": float(profile.get("credit_score", 700)),
        "relationship_months": float(profile.get("relationship_months", 0)),
        "num_products": float(len(profile.get("existing_products", []))),
        "eligible_top": 1.0 if reco.get("eligible") else 0.0,
        "headroom_ratio": headroom / max(1.0, est),
        "intent_home": float(ps.get("HOME_LOAN", 0)) / 100.0,
        "intent_auto": float(ps.get("AUTO_LOAN", 0)) / 100.0,
        "intent_personal": float(ps.get("PERSONAL_LOAN", 0)) / 100.0,
        "intent_mortgage": float(ps.get("MORTGAGE_LOAN", 0)) / 100.0,
        "sig_renter": 1.0 if sig.get("is_renter") else 0.0,
        "sig_sip_rising": 1.0 if sig.get("sip_rising") else 0.0,
        "sig_auto_booking": 1.0 if sig.get("auto_booking") else 0.0,
        "sig_big_expense": 1.0 if sig.get("big_expense_recent") else 0.0,
        "sig_high_cc": 1.0 if sig.get("high_cc_utilization") else 0.0,
        "sig_business_growth": 1.0 if sig.get("business_growth") else 0.0,
        "sig_liquidity_tightening": 1.0 if sig.get("liquidity_tightening") else 0.0,
    }


def lead_quality_score(profile: Dict, income: Dict, afford: Dict, intent: Dict) -> Dict:
    intent_pts = 0.40 * float(intent.get("top_score", 0))              # 0-40
    income_pts = 20.0 * float(income.get("confidence", 0))            # 0-20
    afford_pts = float(GRADE_PTS.get(afford.get("grade", "NA"), 5))    # 0-25
    score = float(profile.get("credit_score", 700))
    profile_pts = (10 * np.clip((score - 550) / 300, 0, 1)
                   + 3 * np.clip(profile.get("relationship_months", 0) / 60, 0, 1)
                   + 2 * np.clip(len(profile.get("existing_products", [])) / 3, 0, 1))  # 0-15
    total = float(intent_pts + income_pts + afford_pts + profile_pts)
    return {
        "lead_quality_score": round(total, 1),
        "components": {
            "intent": round(intent_pts, 1),
            "income_confidence": round(income_pts, 1),
            "affordability": round(afford_pts, 1),
            "profile": round(float(profile_pts), 1),
        },
    }
