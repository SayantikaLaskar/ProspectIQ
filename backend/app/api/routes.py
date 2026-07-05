"""HTTP API for the Prospect IQ dashboard."""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.agents import orchestrator
from app.agents.llm import llm
from app.agents.pitch import CHANNELS, generate_pitch
from app.constants import PRODUCTS
from app.leads import lead_service

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = None


class PitchRequest(BaseModel):
    channel: str = "WHATSAPP"


@router.get("/health")
def health():
    return {"status": "ok", "ready": lead_service.ready, "llm": llm.info()}


@router.get("/meta")
def meta():
    return {
        "products": [{"code": c, "label": p["label"], "annual_rate": p["annual_rate"]}
                     for c, p in PRODUCTS.items()],
        "bands": ["HOT", "WARM", "NURTURE", "COLD"],
        "channels": CHANNELS,
        "llm": llm.info(),
        "total_customers": lead_service.metrics.get("total_customers"),
    }


@router.get("/impact")
def impact():
    return lead_service.metrics


@router.get("/leads")
def leads(
    product: Optional[str] = Query(None),
    band: Optional[str] = Query(None),
    min_conv: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    return lead_service.list_leads(product=product, band=band, min_conv=min_conv,
                                   search=search, limit=limit, offset=offset)


@router.get("/leads/{customer_id}")
def lead_detail(customer_id: str):
    lead = lead_service.get_lead(customer_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.get("/leads/{customer_id}/agents")
def lead_agents(customer_id: str, channel: str = Query("WHATSAPP")):
    lead = lead_service.get_lead(customer_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return orchestrator.run_all(lead, channel=channel)


@router.post("/leads/{customer_id}/pitch")
def lead_pitch(customer_id: str, req: PitchRequest):
    lead = lead_service.get_lead(customer_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return generate_pitch(lead, req.channel)


@router.post("/leads/{customer_id}/chat")
def lead_chat(customer_id: str, req: ChatRequest):
    lead = lead_service.get_lead(customer_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return orchestrator.chat(lead, req.question, req.history)
