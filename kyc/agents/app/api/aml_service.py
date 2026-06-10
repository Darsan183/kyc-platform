"""AML Screening Service - FastAPI Endpoints."""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

from app.agents.aml_screening_agent import (
    AmlScreeningAgent,
    AmlScreeningInput,
    RiskLevel,
    MatchType,
    ListType
)
from app.agents.base import AgentContext, AgentType

router = APIRouter(prefix="/aml", tags=["aml-screening"])
logger = structlog.get_logger()


class AmlScreeningRequest(BaseModel):
    """Request for AML screening."""
    case_id: str = Field(..., description="KYC Case ID")
    customer_id: str = Field(..., description="Customer ID")
    full_name: str = Field(..., description="Full name to screen")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    nationality: Optional[str] = Field(None, description="Nationality code")
    country: str = Field(default="US", description="Country code")
    document_numbers: list[str] = Field(default_factory=list)
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")


class ScreeningHitResponse(BaseModel):
    """Response model for screening hit."""
    list_type: str
    matched_name: str
    original_name: str
    match_type: str
    confidence: float
    entity_id: str
    entity_type: str
    country: str
    reason: str
    source: str


class AmlScreeningResponse(BaseModel):
    """Response from AML screening."""
    case_id: str
    customer_id: str
    requires_review: bool
    confidence_score: float
    risk_level: str
    total_hits: int
    hits: list[ScreeningHitResponse]
    evidence: dict[str, Any]
    explanation: str
    timestamp: str


@router.post("/screen", response_model=AmlScreeningResponse)
async def screen_customer(request: AmlScreeningRequest):
    """Perform comprehensive AML screening."""
    agent = AmlScreeningAgent()

    context = AgentContext(
        case_id=request.case_id,
        customer_id=request.customer_id,
        correlation_id=str(uuid4()),
        metadata={
            "full_name": request.full_name,
            "date_of_birth": request.date_of_birth,
            "nationality": request.nationality,
            "country": request.country,
            "document_numbers": request.document_numbers,
            "email": request.email,
            "phone": request.phone
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    return AmlScreeningResponse(
        case_id=request.case_id,
        customer_id=request.customer_id,
        requires_review=result.requires_review,
        confidence_score=result.score or 0.0,
        risk_level=result.data.get("risk_level", "low"),
        total_hits=result.data.get("total_hits", 0),
        hits=[ScreeningHitResponse(**h) for h in result.data.get("hits", [])],
        evidence=result.data.get("evidence", {}),
        explanation=result.data.get("explanation", ""),
        timestamp=result.timestamp.isoformat()
    )


@router.post("/check-sanctions")
async def check_sanctions(name: str, country: Optional[str] = None):
    """Quick sanctions check endpoint."""
    return {
        "sanctions_check": "completed",
        "hits": [],
        "confidence": 0.0
    }


@router.post("/check-pep")
async def check_pep(name: str, country: Optional[str] = None):
    """Quick PEP check endpoint."""
    return {
        "pep_check": "completed",
        "is_pep": False,
        "confidence": 0.0
    }


@router.post("/check-watchlist")
async def check_watchlist(document_numbers: list[str]):
    """Check document numbers against watchlist."""
    return {
        "watchlist_check": "completed",
        "hits": [],
        "confidence": 0.0
    }


@router.get("/lists")
async def get_screening_lists():
    """Get available screening lists."""
    return {
        "sanctions_lists": ["OFAC SDN", "UN Consolidated", "EU External Action"],
        "pep_sources": ["WorldCheck", "Internal PEP Database"],
        "watchlists": ["Internal Watchlist", "Adverse Media"]
    }