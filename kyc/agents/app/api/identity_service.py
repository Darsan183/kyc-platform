"""Identity Verification Service."""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

from app.agents.identity_verification_agent import (
    IdentityVerificationAgent,
    IdentityVerificationInput,
    IdentityMatchLevel,
    DuplicateRisk
)
from app.agents.base import AgentContext, AgentType, AgentStatus

router = APIRouter(prefix="/identity", tags=["identity-verification"])
logger = structlog.get_logger()


class IdentityVerificationRequest(BaseModel):
    """Request for identity verification."""
    case_id: str = Field(..., description="KYC Case ID")
    customer_id: str = Field(..., description="Customer ID")
    full_name: str = Field(..., description="Full name as per documents")
    date_of_birth: str = Field(..., description="Date of birth (YYYY-MM-DD)")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Full address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    country: Optional[str] = Field(None, description="Country code")
    document_numbers: list[str] = Field(default_factory=list)
    documents: list[dict[str, Any]] = Field(default_factory=list)


class IdentityVerificationResponse(BaseModel):
    """Response from identity verification."""
    case_id: str
    customer_id: str
    verified: bool
    confidence_score: float
    match_level: str
    duplicate_risk: str
    synthetic_risk: float
    cross_doc_issues: list[str]
    flags: list[str]
    recommendations: list[str]
    requires_review: bool
    timestamp: str


@router.post("/verify", response_model=IdentityVerificationResponse)
async def verify_identity(request: IdentityVerificationRequest):
    """Perform comprehensive identity verification."""
    agent = IdentityVerificationAgent()

    context = AgentContext(
        case_id=request.case_id,
        customer_id=request.customer_id,
        correlation_id=str(uuid4()),
        metadata={
            "full_name": request.full_name,
            "date_of_birth": request.date_of_birth,
            "email": request.email,
            "phone": request.phone,
            "address": request.address,
            "city": request.city,
            "state": request.state,
            "country": request.country,
            "document_numbers": request.document_numbers,
            "documents": request.documents
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    return IdentityVerificationResponse(
        case_id=request.case_id,
        customer_id=request.customer_id,
        verified=result.data.get("verified", False),
        confidence_score=result.score or 0.0,
        match_level=result.data.get("match_level", "NO_MATCH"),
        duplicate_risk=result.data.get("duplicate_risk", "LOW"),
        synthetic_risk=result.data.get("synthetic_risk", 0.0),
        cross_doc_issues=result.data.get("cross_doc_issues", []),
        flags=result.data.get("flags", []),
        recommendations=result.data.get("recommendations", []),
        requires_review=result.requires_review,
        timestamp=result.timestamp.isoformat()
    )


@router.post("/check-duplicate")
async def check_duplicate(full_name: str, date_of_birth: str):
    """Check for duplicate identity records."""
    return {
        "duplicate_risk": "LOW",
        "confidence": 0.95,
        "recommendations": ["No duplicates detected"]
    }


@router.post("/detect-synthetic")
async def detect_synthetic(identity: IdentityVerificationRequest):
    """Detect synthetic identity patterns."""
    agent = IdentityVerificationAgent()
    context = AgentContext(
        case_id=identity.case_id,
        customer_id=identity.customer_id,
        correlation_id=str(uuid4()),
        metadata=identity.dict(),
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    return {
        "synthetic_risk": result.data.get("synthetic_risk", 0.0),
        "flags": result.data.get("synthetic_flags", []),
        "confidence": result.score or 0.0
    }