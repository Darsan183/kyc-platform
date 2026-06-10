"""State Model for Agent Orchestration."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.agents.base import AgentStatus, AgentType, AgentResult


@dataclass
class CaseState:
    """State model for KYC case processing."""

    # Identifiers
    case_id: str
    customer_id: str
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Current state
    current_agent: Optional[AgentType] = None
    status: AgentStatus = AgentStatus.IDLE
    progress: float = 0.0

    # Agent results
    document_result: Optional[AgentResult] = None
    identity_result: Optional[AgentResult] = None
    aml_result: Optional[AgentResult] = None
    media_result: Optional[AgentResult] = None
    compliance_result: Optional[AgentResult] = None
    risk_result: Optional[AgentResult] = None
    audit_result: Optional[AgentResult] = None

    # Final decision
    final_risk_score: Optional[float] = None
    final_decision: Optional[str] = None
    decision_reason: Optional[str] = None

    # Timestamps
    started_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # Metadata
    customer_data: dict[str, Any] = field(default_factory=dict)
    workflow_data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def get_result(self, agent_type: AgentType) -> Optional[AgentResult]:
        """Get result for specific agent."""
        return getattr(self, f"{agent_type.value}_result", None)

    def set_result(self, result: AgentResult) -> None:
        """Set result for agent."""
        setattr(self, f"{result.agent_type.value}_result", result)
        self.updated_at = datetime.utcnow()

    def add_error(self, error: str) -> None:
        """Add error to state."""
        self.errors.append(error)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "case_id": self.case_id,
            "customer_id": self.customer_id,
            "correlation_id": self.correlation_id,
            "current_agent": self.current_agent.value if self.current_agent else None,
            "status": self.status.value,
            "progress": self.progress,
            "final_risk_score": self.final_risk_score,
            "final_decision": self.final_decision,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "errors": self.errors,
            "customer_data": self.customer_data
        }