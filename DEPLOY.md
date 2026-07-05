# Deploying Prospect IQ

**Frontend → Vercel** (static Vite SPA) · **Backend → Render** (free Docker web service).

The backend runs in **serve mode**: it loads `backend/data_store/precomputed_*.json` (built by `scripts/precompute.py`) instead of training at startup — so it boots in seconds on a 512 MB free tier, while live LLM agent/chat calls still hit Hugging Face using your token.

---

## 1 · Backend on Render (free)

1. Go to **render.com** → **New → Blueprint** → connect this GitHub repo. Render reads `render.yaml`.
2. It creates a Docker web service `prospectiq-api` (root dir `backend`). When prompted, set the secret:
   - **`HF_API_TOKEN`** = your Hugging Face token (`hf_…`).
   *(the other env vars — `LLM_PROVIDER`, `HF_MODEL`, `CORS_ORIGINS` — are preset in `render.yaml`.)*
3. **Apply / Deploy.** After ~3–5 min you get a URL like `https://prospectiq-api.onrender.com`.
4. Test it: open `https://prospectiq-api.onrender.com/api/health` → should return `{"status":"ok",...}`.

> Manual alternative: **New → Web Service** → this repo → Root Directory `backend`, Runtime `Docker` → add the env vars above → Create.
>
> ⚠️ Free tier sleeps after ~15 min idle; the first request then takes ~30–60 s to wake. That's normal. (Upgrade to the $7 plan for always-on.)

## 2 · Frontend on Vercel

1. Go to **vercel.com** → **Add New → Project** → import this repo.
2. Set **Root Directory = `frontend`** (Framework auto-detects as **Vite**).
3. Add an **Environment Variable**:
   - **`VITE_API_URL`** = your Render backend URL (e.g. `https://prospectiq-api.onrender.com`) — **no trailing slash**.
4. **Deploy.** Open the Vercel URL — you're live.

## 3 · Verify end-to-end
- Landing loads, the hero card cycles through live leads.
- Dashboard KPIs populate (they're fetched from the Render backend via `VITE_API_URL`).
- Open a lead → the AI Copilot shows `huggingface · meta-llama/Llama-3.1-8B-Instruct` and generates live prose.

---

## Notes
- **Secrets:** `HF_API_TOKEN` lives only in the Render dashboard. `backend/.env` is git-ignored and never pushed.
- **Regenerate data** (after changing engines/generator): `cd backend && ./.venv/bin/python scripts/precompute.py`, then commit the updated `backend/data_store/precomputed_*.json` and redeploy.
- **Rotate your HF token** after the event (it was shared in chat during setup).
- **Other hosts:** the `backend/Dockerfile` also runs as-is on Railway, Fly.io, or Google Cloud Run — point them at `backend/` and set the same env vars.
