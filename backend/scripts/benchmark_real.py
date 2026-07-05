"""Real-data benchmark for the conversion-modeling approach.

Validates on the UCI Bank Marketing dataset (real Portuguese-bank telemarketing
conversions, n=45,211). We report AUC in the *pre-contact* setting — i.e. with
the `duration` feature dropped, because call duration is only known AFTER the
call and would leak the outcome. That's the honest analogue of scoring a lead
BEFORE the RM reaches out, which is exactly our use case.

Writes data_store/real_benchmark.json so the dashboard can surface it.
"""
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from app.config import settings

CSV = settings.DATA_DIR / "bank-full.csv"
OUT = settings.DATA_DIR / "real_benchmark.json"


def _auc(df: pd.DataFrame, y, drop_duration: bool) -> float:
    X = df.drop(columns=["y"] + (["duration"] if drop_duration else []))
    X = pd.get_dummies(X, drop_first=True).astype(float)
    clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, random_state=0)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    proba = cross_val_predict(clf, X.values, y, cv=cv, method="predict_proba")[:, 1]
    return float(roc_auc_score(y, proba))


def run() -> dict:
    df = pd.read_csv(CSV, sep=";")
    y = (df["y"] == "yes").astype(int).values
    res = {
        "dataset": "UCI Bank Marketing (bank-full.csv)",
        "n": int(len(df)),
        "positive_rate": round(float(y.mean()), 4),
        "auc_precontact": round(_auc(df, y, drop_duration=True), 4),
        "auc_with_duration": round(_auc(df, y, drop_duration=False), 4),
    }
    OUT.write_text(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
