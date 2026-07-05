"""Lead service: run every customer through the engines + model, rank, cache,
and answer the queries the API needs (queue, detail, impact metrics).

Built once at startup and held in memory so the dashboard is instant.
"""
import json
from collections import Counter
from typing import Dict, List, Optional

import numpy as np

from app.config import settings
from app.data.store import store
from app.engines import scoring
from app.engines.affordability import assess_affordability
from app.engines.income import estimate_income
from app.engines.intent import detect_intent
from app.ml.conversion_model import ConversionModel

QUALIFY = 0.30  # predicted-conversion cut-off for "surfaced" leads (the KPI)
PRECOMP_LEADS = settings.DATA_DIR / "precomputed_leads.json"
PRECOMP_METRICS = settings.DATA_DIR / "precomputed_metrics.json"


def _band(p: float) -> str:
    if p >= 0.50:
        return "HOT"
    if p >= 0.30:
        return "WARM"
    if p >= 0.15:
        return "NURTURE"
    return "COLD"


class LeadService:
    def __init__(self) -> None:
        self.leads: List[Dict] = []
        self.by_id: Dict[str, Dict] = {}
        self.model: Optional[ConversionModel] = None
        self.metrics: Dict = {}
        self.features_by_id: Dict[str, List[float]] = {}
        self.ready = False
        self._precomputed = False

    # ------------------------------------------------------------------ #
    def build(self) -> None:
        """Load precomputed leads if present (deploy/serve mode), else build fresh."""
        if PRECOMP_LEADS.exists() and PRECOMP_METRICS.exists():
            self._load_precomputed()
            return
        self._full_build()

    def _load_precomputed(self) -> None:
        self.leads = json.loads(PRECOMP_LEADS.read_text())
        self.by_id = {l["customer_id"]: l for l in self.leads}
        self.metrics = json.loads(PRECOMP_METRICS.read_text())
        self._precomputed = True
        self.ready = True

    def _full_build(self) -> None:
        store.ensure_loaded()
        rows, feats, y, credit, declared = [], [], [], [], []
        for c in store.customers:
            cid = c["customer_id"]
            tx = store.txns(cid)
            income = estimate_income(c, tx)
            afford = assess_affordability(c, tx, income)
            intent = detect_intent(c, tx, income)
            reco = scoring.recommend_product(intent, afford)
            f = scoring.build_features(c, income, afford, intent, reco)
            q = scoring.lead_quality_score(c, income, afford, intent)
            rows.append((c, income, afford, intent, reco, q, f))
            feats.append([f[k] for k in scoring.FEATURE_NAMES])
            y.append(int(store.ground_truth.get(cid, {}).get("would_convert", False)))
            credit.append(c["credit_score"])
            declared.append(c["declared_monthly_income"])

        X = np.array(feats, dtype=float)
        self.model = ConversionModel(scoring.FEATURE_NAMES).fit(X, y)
        proba = self.model.oof_proba if self.model.oof_proba is not None else self.model.predict_proba(X)

        for i, (c, income, afford, intent, reco, q, f) in enumerate(rows):
            pc = float(proba[i])
            cid = c["customer_id"]
            self.features_by_id[cid] = feats[i]
            self.leads.append({
                "customer_id": cid,
                "name": c["name"],
                "age": c["age"],
                "gender": c.get("gender"),
                "city": c["city"],
                "city_tier": c["city_tier"],
                "employment_type": c["employment_type"],
                "credit_score": c["credit_score"],
                "relationship_months": c["relationship_months"],
                "existing_products": c["existing_products"],
                "declared_monthly_income": c["declared_monthly_income"],
                "estimated_monthly_income": income["estimated_monthly_income"],
                "income_confidence": income["confidence"],
                "income_type": income["income_type"],
                "income_uplift_pct": income.get("income_uplift_pct", 0.0),
                "affordability_grade": afford["grade"],
                "foir_existing": afford["foir_existing"],
                "disposable_income": afford["disposable_income"],
                "predicted_conversion": round(pc, 4),
                "band": _band(pc),
                "lead_quality_score": q["lead_quality_score"],
                "score_components": q["components"],
                "recommended_product": reco["product"],
                "recommended_product_label": reco["label"],
                "recommended_amount": reco["recommended_amount"],
                "indicative_emi": reco["indicative_emi"],
                "annual_rate": reco["annual_rate"],
                "tenure_months": reco["tenure_months"],
                "under_review": reco["under_review"],
                "top_intent_score": intent.get("top_score", 0),
                "why_now": intent.get("why_now"),
                # full engine payloads (served on detail)
                "income": income,
                "affordability": afford,
                "intent": intent,
            })

        self.leads.sort(key=lambda l: l["predicted_conversion"], reverse=True)
        self.by_id = {l["customer_id"]: l for l in self.leads}
        self._compute_metrics(np.asarray(y), np.asarray(proba),
                              np.asarray(credit, dtype=float), np.asarray(declared, dtype=float))
        self.metrics["validation"] = self._validation()
        rb = settings.DATA_DIR / "real_benchmark.json"
        if rb.exists():
            try:
                self.metrics["real_benchmark"] = json.loads(rb.read_text())
            except Exception:
                pass
        self.ready = True

    # ------------------------------------------------------------------ #
    def _compute_metrics(self, y, proba, credit, declared) -> None:
        n = int(y.size)
        base = float(y.mean()) if n else 0.0
        qmask = proba >= QUALIFY
        qual_conv = float(y[qmask].mean()) if qmask.sum() else 0.0

        def topn_rate(scores, k):
            idx = np.argsort(-scores)[:k]
            return float(y[idx].mean()) if len(idx) else 0.0

        # Same-budget comparison: what converts if an RM can only call K people?
        focus = min(200, n)
        budgets = [b for b in [50, 100, 150, 200, 300, 400] if b <= n]
        curve = [{
            "budget": b,
            "prospect_iq": round(topn_rate(proba, b), 4),
            "by_credit_score": round(topn_rate(credit, b), 4),
            "by_declared_income": round(topn_rate(declared, b), 4),
            "random": round(base, 4),
        } for b in budgets]

        opp = sum(l["recommended_amount"] for l in self.leads
                  if l["predicted_conversion"] >= QUALIFY and l["recommended_amount"])
        dist = Counter(l["recommended_product"] for l in self.leads
                       if l["predicted_conversion"] >= QUALIFY)

        self.metrics = {
            "total_customers": n,
            "baseline_conversion": round(base, 4),
            "qualify_threshold": QUALIFY,
            "qualified_leads": int(qmask.sum()),
            "qualified_conversion": round(qual_conv, 4),
            "conversion_lift_x": round(qual_conv / base, 2) if base > 0 else None,
            "hot_conversion": round(float(y[proba >= 0.5].mean()), 4) if (proba >= 0.5).sum() else 0.0,
            "cold_conversion": round(float(y[proba < 0.15].mean()), 4) if (proba < 0.15).sum() else 0.0,
            "model_auc": round(self.model.auc, 4) if self.model and self.model.auc else None,
            "conversion_drivers": self.model.importances if self.model else {},
            "loan_book_opportunity": int(opp),
            "product_distribution": dict(dist),
            "bands": {b: int(sum(1 for l in self.leads if l["band"] == b))
                      for b in ["HOT", "WARM", "NURTURE", "COLD"]},
            "targeting_focus_budget": int(focus),
            "targeting_comparison": {
                "prospect_iq": round(topn_rate(proba, focus), 4),
                "by_credit_score": round(topn_rate(credit, focus), 4),
                "by_declared_income": round(topn_rate(declared, focus), 4),
                "random": round(base, 4),
            },
            "targeting_curve": curve,
        }

    def _validation(self) -> Dict:
        """Accuracy vs held-out ground truth — the credibility numbers for the
        dashboard (income estimation & intent recall)."""
        gt = store.ground_truth
        eng = {"all": [], "salaried": [], "self_employed": [], "mixed": []}
        dec = {"all": [], "salaried": [], "self_employed": [], "mixed": []}
        hit = tot = top2 = 0
        for l in self.leads:
            g = gt.get(l["customer_id"])
            if not g:
                continue
            t = g["true_monthly_income"]
            if t > 0:
                emp = l["employment_type"]
                eng["all"].append(abs(l["estimated_monthly_income"] - t) / t)
                dec["all"].append(abs(l["declared_monthly_income"] - t) / t)
                eng[emp].append(abs(l["estimated_monthly_income"] - t) / t)
                dec[emp].append(abs(l["declared_monthly_income"] - t) / t)
            if g.get("intent_product"):
                tot += 1
                ps = l["intent"]["product_scores"]
                ranked = sorted(ps, key=lambda k: ps[k], reverse=True)
                hit += int(l["intent"]["top_product"] == g["intent_product"])
                top2 += int(g["intent_product"] in ranked[:2])

        def med(a):
            return round(float(np.median(a)) * 100, 1) if a else None

        return {
            "income_median_ape": {"engine": med(eng["all"]), "declared": med(dec["all"])},
            "income_self_employed_ape": {"engine": med(eng["self_employed"]),
                                         "declared": med(dec["self_employed"])},
            "intent_top1_accuracy": round(hit / tot * 100, 1) if tot else None,
            "intent_top2_accuracy": round(top2 / tot * 100, 1) if tot else None,
            "intent_labeled": tot,
        }

    # ------------------------------------------------------------------ #
    _SUMMARY_KEYS = [
        "customer_id", "name", "age", "city", "city_tier", "employment_type",
        "credit_score", "declared_monthly_income", "estimated_monthly_income",
        "income_confidence", "income_type", "income_uplift_pct", "affordability_grade",
        "foir_existing", "predicted_conversion", "band", "lead_quality_score",
        "score_components", "recommended_product", "recommended_product_label",
        "recommended_amount", "indicative_emi", "annual_rate", "tenure_months",
        "under_review", "top_intent_score", "why_now",
    ]

    def _summary(self, lead: Dict) -> Dict:
        return {k: lead[k] for k in self._SUMMARY_KEYS}

    def list_leads(self, product=None, band=None, min_conv=None, search=None,
                   limit=50, offset=0) -> Dict:
        res = self.leads
        if product:
            res = [l for l in res if l["recommended_product"] == product]
        if band:
            res = [l for l in res if l["band"] == band]
        if min_conv is not None:
            res = [l for l in res if l["predicted_conversion"] >= min_conv]
        if search:
            s = search.lower()
            res = [l for l in res if s in l["name"].lower() or s in l["customer_id"].lower()]
        total = len(res)
        page = [self._summary(l) for l in res[offset: offset + limit]]
        return {"total": total, "limit": limit, "offset": offset, "leads": page}

    def get_lead(self, customer_id: str) -> Optional[Dict]:
        lead = self.by_id.get(customer_id)
        if not lead:
            return None
        if self._precomputed:
            return lead  # already full detail incl recent_transactions
        detail = dict(lead)
        tx = store.txns(customer_id)
        if tx is not None and not tx.empty:
            sample = tx.sort_values("date").tail(12)[
                ["date", "amount", "category", "channel", "narration", "balance"]].copy()
            sample["date"] = sample["date"].dt.strftime("%Y-%m-%d")
            detail["recent_transactions"] = sample.to_dict("records")
        return detail


lead_service = LeadService()
