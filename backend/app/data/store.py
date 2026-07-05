"""Persistence + in-memory access for the synthetic dataset.

Generates once, caches to disk, and serves fast per-customer transaction
slices to the engines.
"""
import json
from typing import Dict, List, Optional

import pandas as pd

from app.config import settings
from app.data.generator import generate_dataset

CUSTOMERS_F = settings.DATA_DIR / "customers.json"
TXNS_F = settings.DATA_DIR / "transactions.pkl"
GT_F = settings.DATA_DIR / "ground_truth.json"


class DataStore:
    def __init__(self) -> None:
        self.customers: List[Dict] = []
        self.customers_by_id: Dict[str, Dict] = {}
        self.transactions: Optional[pd.DataFrame] = None
        self.ground_truth: Dict[str, Dict] = {}
        self._by_customer: Dict[str, pd.DataFrame] = {}

    # ------------------------------------------------------------------ #
    def exists(self) -> bool:
        return CUSTOMERS_F.exists() and TXNS_F.exists() and GT_F.exists()

    def generate(self, num_customers: int, seed: int, force: bool = False) -> None:
        if self.exists() and not force:
            return
        ds = generate_dataset(num_customers, seed)
        CUSTOMERS_F.write_text(json.dumps(ds["customers"]))
        GT_F.write_text(json.dumps(ds["ground_truth"]))
        df = pd.DataFrame(ds["transactions"])
        df["date"] = pd.to_datetime(df["date"])
        df.to_pickle(TXNS_F)

    def load(self) -> None:
        self.customers = json.loads(CUSTOMERS_F.read_text())
        self.customers_by_id = {c["customer_id"]: c for c in self.customers}
        self.ground_truth = json.loads(GT_F.read_text())
        self.transactions = pd.read_pickle(TXNS_F)
        self._by_customer = {
            cid: g.sort_values("date").reset_index(drop=True)
            for cid, g in self.transactions.groupby("customer_id")
        }

    def ensure_loaded(self) -> None:
        if not self.exists():
            self.generate(settings.NUM_CUSTOMERS, settings.RANDOM_SEED)
        if not self.customers:
            self.load()

    def txns(self, customer_id: str) -> pd.DataFrame:
        empty = self.transactions.iloc[0:0] if self.transactions is not None else pd.DataFrame()
        return self._by_customer.get(customer_id, empty)


store = DataStore()
