"""End-to-end validation of the whole intelligence pipeline against held-out
ground truth. Prints the headline numbers we quote in the demo / README.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from app.config import settings
from app.data.store import store
from app.leads import lead_service

store.generate(settings.NUM_CUSTOMERS, settings.RANDOM_SEED, force=True)
store.load()
lead_service.build()
m = lead_service.metrics
tc = m["targeting_comparison"]

print("=" * 60)
print(" PROSPECT IQ — PIPELINE VALIDATION  (n=%d)" % m["total_customers"])
print("=" * 60)
print("Model AUC (out-of-fold)   : %s" % m["model_auc"])
print("Baseline conversion (all) : %.1f%%" % (m["baseline_conversion"] * 100))
print("HOT-band conversion       : %.1f%%" % (m["hot_conversion"] * 100))
print("COLD-band conversion      : %.1f%%" % (m["cold_conversion"] * 100))
print("Qualified leads (>=30%%)    : %d  ->  %.1f%% convert  (lift %.1fx)"
      % (m["qualified_leads"], m["qualified_conversion"] * 100, m["conversion_lift_x"]))
print("-" * 60)
print(" SAME-BUDGET TARGETING  (call the top %d customers)" % m["targeting_focus_budget"])
print("   Random / call-everyone : %.1f%%" % (tc["random"] * 100))
print("   Rank by declared income: %.1f%%" % (tc["by_declared_income"] * 100))
print("   Rank by credit score   : %.1f%%" % (tc["by_credit_score"] * 100))
print("   Prospect IQ            : %.1f%%   <== " % (tc["prospect_iq"] * 100))
print("-" * 60)
print("Loan-book opportunity     : Rs %s" % f"{m['loan_book_opportunity']:,}")
print("Lead bands                : %s" % m["bands"])
print("Qualified product mix     : %s" % m["product_distribution"])

# --- intent recall vs ground truth ---
gt = store.ground_truth
hit = tot = top2 = 0
for l in lead_service.leads:
    g = gt[l["customer_id"]]
    if g["intent_product"]:
        tot += 1
        ranked = sorted(l["intent"]["product_scores"],
                        key=lambda k: l["intent"]["product_scores"][k], reverse=True)
        hit += int(l["intent"]["top_product"] == g["intent_product"])
        top2 += int(g["intent_product"] in ranked[:2])
print("Intent top-1 accuracy     : %.1f%%   top-2: %.1f%%  (n=%d)"
      % (hit / tot * 100, top2 / tot * 100, tot))

# --- income accuracy ---
apes, dapes = [], []
for l in lead_service.leads:
    t = gt[l["customer_id"]]["true_monthly_income"]
    apes.append(abs(l["estimated_monthly_income"] - t) / t)
    dapes.append(abs(l["declared_monthly_income"] - t) / t)
print("Income median APE         : engine %.1f%%   declared %.1f%%"
      % (np.median(apes) * 100, np.median(dapes) * 100))
print("=" * 60)
