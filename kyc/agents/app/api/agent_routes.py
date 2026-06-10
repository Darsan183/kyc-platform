"""Agent API Routes."""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.orchestrator import AgentOrchestrator
from app.agents.base import AgentType, AgentStatus, AgentContext
from app.models.state import CaseState

router = APIRouter()


class AgentExecuteRequest(BaseModel):
    """Request model for agent execution."""
    case_id: str
    customer_id: str
    agent_type: AgentType
    customer_data: dict[str, Any] = Field(default_factory=dict)


class AgentExecuteResponse(BaseModel):
    """Response model for agent execution."""
    case_id: str
    agent_type: str
    status: str
    score: Optional[float] = None
    data: Optional[dict[str, Any]] = None
    errors: Optional[list[str]] = None
    timestamp: str


@router.post("/execute", response_model=AgentExecuteResponse)
async def execute_agent(request: AgentExecuteRequest):
    """Execute a specific agent."""
    orchestrator = AgentOrchestrator()
    
    context = AgentContext(
        case_id=request.case_id,
        customer_id=request.customer_id,
        correlation_id=str(uuid4()),
        metadata=request.customer_data,
        timestamp=datetime.utcnow()
    )

    agent = orchestrator.agents.get(request.agent_type)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {request.agent_type}")

    result = await agent.execute(context)

    return AgentExecuteResponse(
        case_id=request.case_id,
        agent_type=result.agent_type.value,
        status=result.status.value,
        score=result.score,
        data=result.data,
        errors=result.errors,
        timestamp=result.timestamp.isoformat()
    )


@router.get("/status/{case_id}")
async def get_agent_status(case_id: str):
    """Get current agent status for case."""
    return {"case_id": case_id, "status": "implemented"}


@router.get("/types")
async def get_agent_types():
    """List available agent types."""
    return {"types": [t.value for t in AgentType]}