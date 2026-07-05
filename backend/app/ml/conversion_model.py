"""Lead -> conversion probability model.

Gradient-boosted trees over the engineered features (captures the non-linear
interactions between intent, affordability and verifiable income). We use
5-fold out-of-fold predictions for every customer so the reported conversion
metrics -- and the numbers shown in the app -- are honest out-of-sample
estimates rather than in-sample optimism. Global feature importances give a
transparent "what drives conversion" view.
"""
from typing import Dict, List

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_predict


class ConversionModel:
    def __init__(self, feature_names: List[str]) -> None:
        self.feature_names = feature_names
        self.clf = GradientBoostingClassifier(
            random_state=0, n_estimators=250, max_depth=3,
            learning_rate=0.05, subsample=0.9)
        self.oof_proba = None
        self.auc = None
        self.importances: Dict[str, float] = {}
        self.fitted = False

    def fit(self, X: np.ndarray, y: List[int]) -> "ConversionModel":
        y = np.asarray(y).astype(int)
        if len(np.unique(y)) > 1:
            try:
                self.oof_proba = cross_val_predict(
                    self.clf, X, y, cv=5, method="predict_proba")[:, 1]
                self.auc = float(roc_auc_score(y, self.oof_proba))
            except Exception:
                self.oof_proba = None
        self.clf.fit(X, y)
        self.importances = {
            n: round(float(i), 4)
            for n, i in sorted(zip(self.feature_names, self.clf.feature_importances_),
                               key=lambda t: -t[1])
        }
        self.fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.clf.predict_proba(X)[:, 1]
