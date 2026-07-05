"""Prospect IQ — FastAPI application entry point.

Builds the lead intelligence once on startup (engines + model over all
customers) and holds it in memory so the dashboard is instant.
"""
import warnings

warnings.filterwarnings("ignore")  # silence LibreSSL/urllib3 + sklearn notices

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings
from app.data.store import store
from app.leads import lead_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not lead_service.ready:
        lead_service.build()  # loads precomputed JSON in deploy mode, else builds fresh
    m = lead_service.metrics
    print(
        "\n  ⚡ Prospect IQ ready"
        f"\n     customers       : {m.get('total_customers')}"
        f"\n     qualified leads : {m.get('qualified_leads')} @ "
        f"{round(m.get('qualified_conversion', 0) * 100, 1)}% conversion "
        f"({m.get('conversion_lift_x')}x lift)"
        f"\n     agents          : {settings.LLM_PROVIDER}"
        "\n     API docs        : http://localhost:8000/docs\n",
        flush=True,
    )
    yield


app = FastAPI(
    title="Prospect IQ API",
    version="1.0.0",
    description="Cashflow-intelligence lead engine + agentic RM copilot for IDBI retail lending.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # public demo API (no cookies/credentials) — any frontend origin
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"name": "Prospect IQ", "docs": "/docs", "api_base": "/api",
            "ready": lead_service.ready}
