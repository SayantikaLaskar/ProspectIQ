# Prospect IQ — Cashflow-Intelligence Lead Engine + Agentic RM Copilot

**IDBI Innovate 2026 · Problem Statement 2 — Prospect Assist AI**

> *"Bank's retail lending relies on traditional metrics, resulting in low conversions and limited insight into customer intent. A data-driven approach is needed to identify eligible, quantifiable-repayment-capacity, genuinely-interested prospects using transaction and behavioral insights … generate high-quality leads with a conversion rate exceeding 30%, while accurately assessing borrowers' actual income for prudent underwriting (Personal / Home / Mortgage / Auto loans)."*

Prospect IQ reads a customer's **bank transaction stream** — not their declared income — to find, score, and convert retail-lending prospects, and hands the RM an **agentic copilot** that writes the pitch, prepares objections, runs a compliance guardrail, and drafts an underwriting note.

---

## Why this wins the brief — line by line

| The brief asks for… | Prospect IQ delivers |
|---|---|
| "genuinely interested prospects" | **Intent engine** — per-product propensity from behavioural signals + "why-now" trigger detection |
| "quantifiable repayment capacity" | **Affordability engine** — FOIR, existing obligations, disposable income, per-product eligible amount |
| **"actual income levels"** (the hard one) | **Income-estimation engine** — infers true income from transaction inflows; **~5× more accurate than declared income for the self-employed** |
| "transaction and behavioral insights" | every score is computed from the raw transaction stream, with an evidence trail |
| "prudent underwriting" | **Underwriting-brief agent** + a rule-based **RBI/DPDP compliance guardrail** |
| **"conversion rate exceeding 30%"** | leads gated on Intent × Income × Affordability → **41% conversion on qualified leads, proven out-of-sample** |

---

## Results — validated on held-out ground truth (2,500 synthetic customers, seed 42) **and a real dataset**

| Metric | Prospect IQ | Traditional baseline |
|---|---|---|
| **Income error** (median APE vs true income) | **0.7%** | 3.5% (declared) |
| **Income error, self-employed** | **~8%** | **~42%** (declared) — *~5× better* |
| **Conversion — qualified leads (>30%)** | **50.3%** | 17.4% (call everyone) → **2.9× lift** |
| **Conversion — HOT vs COLD band** | **52.5%** vs 6.5% | — (8× separation) |
| **Same call-budget** (top-200 contacts) | **58%** | 20% credit-score · 15% declared-income |
| Conversion AUC — **synthetic** (5-fold out-of-fold) | **0.81** | — |
| Conversion AUC — **real UCI Bank Marketing** (pre-contact) | **0.80** | 0.94 with leaky call-duration |
| Intent recall (top-1 / top-2) | **86% / 93%** | — |
| Loan-book opportunity surfaced (2,500 customers) | **~₹103 Cr** | — |

> Every synthetic metric is emitted by `/api/impact` — nothing is hard-coded (`python scripts/validate.py`). The real-data benchmark is reproducible with `python scripts/benchmark_real.py` on the UCI Bank Marketing dataset.

## Benchmarks & how we compare to SOTA

- **Income estimation** — our transaction-based estimator hits ~0.7% median error (~8% for the self-employed), in the band of production systems like **Plaid** (~95% salary-stream detection). Declared income is off ~42% for the self-employed.
- **Conversion propensity** — **AUC 0.81 on synthetic** and **0.80 on the real UCI Bank Marketing dataset**, in the honest *pre-contact* setting (we drop `duration`, which leaks the outcome). Published boosted-tree scores of ~0.90–0.99 rely on that leaky feature; ours reflect scoring a lead *before* the call — the real use case.
- **Cashflow underwriting is the 2025 SOTA direction** — **Experian's** Credit + Cashflow score and **Plaid LendScore** (both 2025) report large accuracy gains from exactly this alternative-data approach. Prospect IQ adds what they don't: per-product **intent + why-now**, an **agentic RM copilot**, and an **auditable RBI/DPDP guardrail**.
- **Why no fully-real dataset?** No public dataset carries transaction streams **+** loan-conversion **+** true income together — that data is proprietary (exactly why IDBI ships a sandbox). So we use a privacy-safe synthetic generator for the transaction pipeline and validate the conversion model on real UCI data. Swap in IDBI sandbox / Account-Aggregator data by changing one module.

---

## How it works

```
                 ┌──────────────────────────────────────────────────────────┐
                 │            Transaction stream (12 months / customer)       │
                 │   salary • UPI inflows • EMIs • rent • SIP • cash • spends  │
                 └──────────────────────────────────────────────────────────┘
                          │                 │                 │
                 ┌────────▼──────┐ ┌─────────▼───────┐ ┌───────▼────────┐
                 │ Income engine │ │  Affordability  │ │  Intent engine │
                 │ true income,  │ │ FOIR, disposable│ │ per-product     │
                 │ type, conf.   │ │ eligible amount │ │ propensity+why-now│
                 └────────┬──────┘ └─────────┬───────┘ └───────┬────────┘
                          └────────────┬─────┴──────────────────┘
                                ┌──────▼───────┐
                                │  Fusion +     │  Gradient-boosted conversion
                                │  ML scoring   │  model (out-of-fold calibrated)
                                └──────┬───────┘
                    ┌──────────────────┼───────────────────┐
            ┌───────▼────────┐  ┌──────▼──────┐    ┌────────▼─────────┐
            │ Ranked lead     │  │  Agentic    │    │ Impact dashboard  │
            │ queue + scores  │  │  RM copilot │    │ (proves >30% KPI) │
            └─────────────────┘  └─────────────┘    └───────────────────┘
                                        │
        Analyst brief · Personalised pitch (SMS/WhatsApp/Email/Call) ·
        Objection handling · RBI/DPDP compliance guardrail · Underwriting brief · RM chat
```

**Agentic layer** = 5 role-specialised agents + an orchestrator. It runs **fully offline on deterministic templates (zero API keys)** so the demo never breaks, and upgrades to real generation when a free **Hugging Face / Groq / Ollama** provider is configured.

---

## Quick start

```bash
# from the project root
./run.sh
```

Then open **http://localhost:5173**. First run seeds synthetic data and trains the model (~30s for 2,500 customers).

<details>
<summary>Manual (two terminals)</summary>

**Backend**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000          # http://localhost:8000/docs
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                                # http://localhost:5173
```
</details>

### Optional: turn on a real LLM (still free)
Copy `backend/.env.example` → `backend/.env` and set one of:
```env
LLM_PROVIDER=huggingface     # + HF_API_TOKEN=hf_xxx   (free: huggingface.co/settings/tokens)
LLM_PROVIDER=groq            # + GROQ_API_KEY=gsk_xxx   (free: console.groq.com)
LLM_PROVIDER=ollama          # local, no key
```
Default `template` needs **no keys** and runs everything end-to-end.

---

## Tech stack
- **Backend:** Python · FastAPI · pandas · scikit-learn (Gradient Boosting) — API-first, deployable into a bank sandbox
- **Frontend:** React + TypeScript + Vite + Tailwind + Recharts
- **Agents:** provider-agnostic LLM client (HuggingFace / Groq / Ollama) with deterministic template fallback
- **Data:** privacy-safe synthetic generator (mapped to IDBI's sandbox schema — transactions / UPI / MSME cashflow)

## Project structure
```
backend/
  app/
    data/generator.py     synthetic Indian retail-banking data + ground truth
    data/store.py         persistence + fast per-customer slices
    engines/income.py     income estimation from inflows
    engines/affordability.py  FOIR / eligibility
    engines/intent.py     propensity + why-now triggers
    engines/scoring.py    fusion + transparent lead score
    ml/conversion_model.py  gradient-boosted conversion model (OOF calibrated)
    agents/               analyst · pitch · objections · compliance · underwriting · orchestrator
    leads.py              orchestration, ranking, impact metrics
    api/routes.py         REST API
  scripts/validate.py     reproduces every headline metric
frontend/src/             dashboard · lead queue · lead workspace · chat copilot
```

## Responsible AI & compliance
- **Explainable by design** — every score carries an evidence trail; the lead score is a transparent factor blend; conversion drivers are shown as feature importances.
- **Auditable compliance** — the guardrail is rule-based (not generative): DPDP consent, product suitability / no mis-selling, responsible-lending capacity, transparent RBI fair-practice pricing, prohibited-claim screening of every outbound message.
- **Privacy-safe** — trained and demoed entirely on synthetic data; uses only the bank's own transaction data under the customer relationship.

## Roadmap → IDBI integration
1. Swap the synthetic generator for IDBI sandbox APIs / Account-Aggregator (AA) consented data (same schema).
2. Feed real historical conversions to retrain the model on live outcomes.
3. Push qualified leads + underwriting briefs into the RM CRM / LOS; close the loop on actual conversions.

*Built for IDBI Innovate 2026 — "Build. Integrate. Transform."*
