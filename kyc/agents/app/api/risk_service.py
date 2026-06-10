"""Risk Scoring Service - FastAPI Endpoints."""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

from app.agents.risk_scoring_engine import RiskScoringEngine, RiskLevel
from app.agents.base import AgentContext

router = APIRouter(prefix="/risk", tags=["risk-scoring"])
logger = structlog.get_logger()


class RiskScoringRequest(BaseModel):
    """Request for risk scoring."""
    case_id: str = Field(..., description="KYC Case ID")
    customer_id: str = Field(..., description="Customer ID")
    identity_score: Optional[int] = Field(100, description="Identity verification score")
    document_score: Optional[int] = Field(100, description="Document verification score")
    aml_hits: int = Field(default=0, description="Number of AML hits")
    aml_risk_level: str = Field(default="low", description="AML risk level")
    media_negative_articles: int = Field(default=0, description="Negative media articles")
    media_total_articles: int = Field(default=0, description="Total media articles")
    compliance_violations: int = Field(default=0, description="Compliance violations")
    country: Optional[str] = Field(None, description="Customer country code")
    weights: Optional[dict[str, float]] = Field(None, description="Custom weights")


class RiskComponentResponse(BaseModel):
    """Response model for risk component."""
    name: str
    score: float
    weight: float
    reasons: list[str]


class RiskScoringResponse(BaseModel):
    """Response from risk scoring."""
    case_id: str
    customer_id: str
    requires_review: bool
    confidence: float
    risk_score: float
    risk_level: str
    decision: str
    reasons: list[str]
    components: list[RiskComponentResponse]
    evidence: dict[str, Any]
    explanation: str
    timestamp: str


@router.post("/calculate", response_model=RiskScoringResponse)
async def calculate_risk(request: RiskScoringRequest):
    """Calculate comprehensive risk score."""
    agent = RiskScoringEngine(config={"weights": request.weights} if request.weights else None)

    context = AgentContext(
        case_id=request.case_id,
        customer_id=request.customer_id,
        correlation_id=str(uuid4()),
        metadata={
            "identity_score": request.identity_score,
            "document_score": request.document_score,
            "aml_hits": request.aml_hits,
            "aml_risk_level": request.aml_risk_level,
            "media_negative_articles": request.media_negative_articles,
            "media_total_articles": request.media_total_articles,
            "compliance_violations": request.compliance_violations,
            "country": request.country
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    return RiskScoringResponse(
        case_id=request.case_id,
        customer_id=request.customer_id,
        requires_review=result.requires_review,
        confidence=result.data.get("confidence", 0.0),
        risk_score=result.score,
        risk_level=result.data.get("risk_level", "low"),
        decision=result.data.get("decision", "APPROVE"),
        reasons=result.data.get("reasons", []),
        components=[RiskComponentResponse(**c) for c in result.data.get("components", [])],
        evidence=result.data.get("evidence", {}),
        explanation=result.data.get("explanation", ""),
        timestamp=result.timestamp.isoformat()
    )


@router.get("/weights")
async def get_weights():
    """Get default risk weights."""
    return {
        "weights": RiskScoringEngine.DEFAULT_WEIGHTS,
        "description": "Default weights for risk scoring components"
    }


@router.post("/custom-weights")
async def calculate_with_custom_weights(
    request: RiskScoringRequest,
    weights: dict[str, float]
):
    """Calculate risk with custom weights."""
    agent = RiskScoringEngine(config={"weights": weights})

    context = AgentContext(
        case_id=request.case_id,
        customer_id=request.customer_id,
        correlation_id=str(uuid4()),
        metadata=request.dict(),
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    return {
        "risk_score": result.score,
        "risk_level": result.data.get("risk_level"),
        "decision": result.data.get("decision")
    }


@router.post("/adjust-score")
async def adjust_score(
    current_score: float,
    country: str,
    additional_factors: Optional[dict[str, Any]] = None
):
    """Get ML-adjusted score for specific factors."""
    # Mock ML adjustment
    high_risk_countries = ["KP", "IR", "SY", "RU"]

    adjusted = current_score
    if country in high_risk_countries:
        adjusted = min(100, current_score + 15)

    return {
        "original_score": current_score,
        "adjusted_score": adjusted,
        "adjustments": {
            "country_risk": country in high_risk_countries,
            "country_factor": 15 if country in high_risk_countries else 0
        }
    }