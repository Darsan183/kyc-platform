"""Adverse Media Service - FastAPI Endpoints."""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

from app.agents.adverse_media_agent import AdverseMediaAgent
from app.agents.adverse_media_agent import (
    MediaRisk,
    Sentiment,
    SourceType
)
from app.agents.base import AgentContext, AgentType

router = APIRouter(prefix="/adverse-media", tags=["adverse-media"])
logger = structlog.get_logger()


class AdverseMediaRequest(BaseModel):
    """Request for adverse media screening."""
    case_id: str = Field(..., description="KYC Case ID")
    customer_id: str = Field(..., description="Customer ID")
    full_name: str = Field(..., description="Full name to screen")
    aliases: list[str] = Field(default_factory=list, description="Alternative names")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    nationality: Optional[str] = Field(None, description="Nationality code")
    country: str = Field(default="US", description="Country code")


class ArticleResponse(BaseModel):
    """Response model for article."""
    id: str
    title: str
    url: str
    source: str
    sentiment: str
    confidence: float
    relevance_score: float


class AdverseMediaResponse(BaseModel):
    """Response from adverse media screening."""
    case_id: str
    customer_id: str
    requires_review: bool
    confidence_score: float
    risk_level: str
    total_articles: int
    negative_articles: int
    avg_sentiment: float
    articles: list[ArticleResponse]
    evidence: dict[str, Any]
    explanation: str
    timestamp: str


@router.post("/screen", response_model=AdverseMediaResponse)
async def screen_media(request: AdverseMediaRequest):
    """Perform adverse media screening."""
    agent = AdverseMediaAgent()

    context = AgentContext(
        case_id=request.case_id,
        customer_id=request.customer_id,
        correlation_id=str(uuid4()),
        metadata={
            "full_name": request.full_name,
            "aliases": request.aliases,
            "date_of_birth": request.date_of_birth,
            "nationality": request.nationality,
            "country": request.country
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    return AdverseMediaResponse(
        case_id=request.case_id,
        customer_id=request.customer_id,
        requires_review=result.requires_review,
        confidence_score=result.score or 0.0,
        risk_level=result.data.get("risk_level", "low"),
        total_articles=result.data.get("total_articles", 0),
        negative_articles=result.data.get("negative_articles", 0),
        avg_sentiment=result.data.get("avg_sentiment", 0.5),
        articles=[ArticleResponse(**a) for a in result.data.get("articles", [])],
        evidence=result.data.get("evidence", {}),
        explanation=result.data.get("explanation", ""),
        timestamp=result.timestamp.isoformat()
    )


@router.post("/search")
async def search_articles(query: str, limit: int = 10):
    """Search articles using RAG/vector search."""
    return {
        "articles": [],
        "query": query,
        "limit": limit
    }


@router.get("/sources")
async def get_sources():
    """Get available news sources."""
    return {
        "sources": ["Reuters", "Associated Press", "BBC", "Local News"],
        "types": [t.value for t in SourceType]
    }


@router.post("/analyze-sentiment")
async def analyze_sentiment(text: str):
    """Analyze sentiment of text."""
    agent = AdverseMediaAgent()
    sentiment = agent._mock_sentiment(text)
    return {
        "text": text,
        "sentiment": sentiment.value,
        "confidence": 0.85
    }