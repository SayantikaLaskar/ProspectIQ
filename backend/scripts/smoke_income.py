"""Quick check: does the income engine beat declared income vs ground truth?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from app.data.generator import generate_dataset
from app.engines.income import estimate_income

ds = generate_dataset(300, 7)
gt = ds["ground_truth"]
custs = {c["customer_id"]: c for c in ds["customers"]}
tx = pd.DataFrame(ds["transactions"])
tx["date"] = pd.to_datetime(tx["date"])
groups = {cid: g for cid, g in tx.groupby("customer_id")}

rows = []
for cid, c in custs.items():
    r = estimate_income(c, groups[cid])
    true = gt[cid]["true_monthly_income"]
    rows.append({
        "emp": c["employment_type"],
        "true": true,
        "declared": c["declared_monthly_income"],
        "est": r["estimated_monthly_income"],
        "ape_est": abs(r["estimated_monthly_income"] - true) / true,
        "ape_declared": abs(c["declared_monthly_income"] - true) / true,
    })
df = pd.DataFrame(rows)
print("=== Median Absolute % Error vs TRUE income ===")
print("Overall  : engine %.1f%%   declared %.1f%%"
      % (df.ape_est.median() * 100, df.ape_declared.median() * 100))
for emp, g in df.groupby("emp"):
    print("  %-13s engine %.1f%%   declared %.1f%%   (n=%d)"
          % (emp, g.ape_est.median() * 100, g.ape_declared.median() * 100, len(g)))
print("\nSample self-employed:")
print(df[df.emp == "self_employed"].head(4).to_string(index=False))
