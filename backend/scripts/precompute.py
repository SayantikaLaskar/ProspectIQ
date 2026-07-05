"""Precompute leads + metrics into JSON for lightweight deployment.

Runs the full pipeline once (engines + model over all customers) locally, then
dumps every lead's full detail and the impact metrics to data_store/*.json. In
production the backend just loads these — instant startup, tiny memory, no
pandas/sklearn model-building on the server (only live LLM agent calls remain).
"""
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from app.config import settings
from app.data.store import store
from app.leads import PRECOMP_LEADS, PRECOMP_METRICS, lead_service


def _default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


def run() -> None:
    store.generate(settings.NUM_CUSTOMERS, settings.RANDOM_SEED)
    store.ensure_loaded()
    lead_service._full_build()  # force the real build (ignore any existing precompute)
    details = [lead_service.get_lead(cid) for cid in lead_service.by_id]
    PRECOMP_LEADS.write_text(json.dumps(details, default=_default))
    PRECOMP_METRICS.write_text(json.dumps(lead_service.metrics, default=_default))
    size = PRECOMP_LEADS.stat().st_size / 1e6
    print(f"✓ precomputed {len(details)} leads ({size:.1f} MB) → {PRECOMP_LEADS.name}")
    print(f"✓ metrics → {PRECOMP_METRICS.name} (AUC {lead_service.metrics.get('model_auc')}, "
          f"{lead_service.metrics.get('qualified_leads')} qualified)")


if __name__ == "__main__":
    run()
