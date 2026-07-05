# Prospect IQ — Demo Script (≈4 minutes)

Open **http://localhost:5173**. Talk track below; numbers are from the bundled dataset.

## 0 · The hook (30s)
> "Banks chase retail-lending leads on declared income and a bureau score — so cold conversion sits in single digits, and self-employed customers get mis-assessed. Prospect IQ reads the **transaction stream** instead. It finds who genuinely wants a loan, proves what they *actually* earn, checks they can repay — and hands the RM an AI copilot to close. Same effort, **~3× the loans**."

## 1 · Business Impact tab (60s) — lead with the money
- **Qualified conversion 50%** vs **17%** baseline → **2.9× lift**, comfortably past the 30% target.
- **"Same call budget" chart:** calling the top 200 customers — Prospect IQ **58%** vs credit-score **20%** vs declared-income **15%**. *"Same 200 calls, we book ~3× the loans."*
- **Income accuracy card:** self-employed income error **42% → 8%** — *"this is 'actual income levels', ~5× better than declared."*
- **Model AUC 0.81** (synthetic) with the sub-line *"real UCI benchmark: 0.80"* — *"validated on real data too, not just our own."*
- Note: *"Every number here is validated against held-out ground truth — nothing hard-coded."*

## 2 · Lead Queue tab (30s)
- Ranked by predicted conversion; **Qualified (>30%)** filter on.
- Point out the **why-now chips** (Salary Hike, EMI Closure, Dealer Enquiry) and the **+% vs declared** income tags.
- Filter by **Home Loan** to show product targeting. Click a HOT self-employed lead.

## 3 · Prospect workspace (90s) — the depth
**Left (the intelligence):**
- **Lead score** — transparent breakdown: Intent / Income confidence / Affordability / Profile.
- **Income estimation** — verified income vs declared with the uplift %, the monthly trend, and the **evidence** ("recurring salary detected in 6/6 months", "variable inflows ₹X/mo, volatility Y%").
- **Repayment capacity** — FOIR, disposable income, and the **per-product eligible amount** table.
- **Buying intent** — per-product bars, the **Why-now** callout, behavioural signal chips.
- Scroll to **recent transactions** — *"the raw evidence it's all built on."*

**Right (the agentic copilot):** click through the tabs —
- **Brief** — plain-English rationale.
- **Pitch** — switch **WhatsApp → Call script**; note it's personalised to the trigger and RBI-compliant (opt-out, no false promises).
- **Compliance** — all-PASS, **rule-based and auditable** (DPDP consent, suitability, fair pricing, prohibited-claim screening).
- **Underwriting** — a PROCEED/REFER recommendation + risk flags → *"prudent underwriting, handed to credit."*
- **Chat** — ask *"What's their real income?"* / *"Any risks?"* — grounded answers.

## 4 · The close (30s)
> "Prospect IQ turns the bank's own transaction data into high-quality, explainable, compliant leads with verified income — hitting 50%+ conversion and surfacing a **₹103 Cr** pipeline from 2,500 customers, with a model validated on real data (AUC 0.80). It's API-first, runs with zero external keys, and drops onto IDBI's sandbox / Account-Aggregator data by swapping one module. Build. Integrate. Transform."

---

## Judge Q&A — quick answers
- **"How do you estimate income?"** Detect recurring salary credits by narration + monthly recurrence; aggregate business/UPI inflows with a volatility haircut; blend, classify (salaried/self-employed/mixed), attach a confidence score. Validated: 0.6% median error overall, 7.8% for self-employed.
- **"Is 30%+ real or cherry-picked?"** Out-of-fold (5-fold CV) conversion model — the reported numbers are out-of-sample. We also show the full budget-vs-conversion curve, not one point.
- **"How accurate is the model?"** AUC **0.81 on synthetic** and **0.80 on the real UCI Bank Marketing dataset** — in the honest *pre-contact* setting (we drop the `duration` feature, which leaks the outcome; with it, AUC is 0.94). Top-decile converts at 52% vs 6.5% bottom — the ranking drives the business case.
- **"Data privacy / RBI?"** Uses only the bank's own transaction data under the customer relationship; compliance guardrail is rule-based and auditable; demo runs on synthetic data.
- **"Cold-start / new customers?"** Flagged as REVIEW by the compliance + eligibility logic; the model degrades gracefully to declared metrics when transaction history is thin.
- **"Does it need a paid LLM?"** No — the agents run on deterministic templates with zero keys; a free HuggingFace/Groq/Ollama key just makes the prose richer.
