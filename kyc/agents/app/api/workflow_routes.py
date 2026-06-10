"""Workflow API Routes."""

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.orchestrator import AgentOrchestrator
from app.models.state import CaseState

router = APIRouter()


class WorkflowExecuteRequest(BaseModel):
    """Request model for workflow execution."""
    case_id: str
    customer_id: str
    customer_data: dict[str, Any] = Field(default_factory=dict)


class WorkflowExecuteResponse(BaseModel):
    """Response model for workflow execution."""
    case_id: str
    customer_id: str
    correlation_id: str
    status: str
    progress: float
    final_risk_score: Optional[float] = None
    final_decision: Optional[str] = None
    errors: list[str] = Field(default_factory=list)
    timestamp: str


@router.post("/process", response_model=WorkflowExecuteResponse)
async def process_workflow(request: WorkflowExecuteRequest):
    """Process a case through all agents."""
    orchestrator = AgentOrchestrator()
    
    state = await orchestrator.process_case(
        request.case_id,
        request.customer_id,
        request.customer_data
    )

    return WorkflowExecuteResponse(
        case_id=state.case_id,
        customer_id=state.customer_id,
        correlation_id=state.correlation_id,
        status=state.status.value,
        progress=state.progress,
        final_risk_score=state.final_risk_score,
        final_decision=state.final_decision,
        errors=state.errors,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/state/{case_id}")
async def get_workflow_state(case_id: str):
    """Get workflow state for case."""
    return {"case_id": case_id, "state": "pending_implementation"}