"""Agent Base Classes and Interfaces."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"


class AgentType(str, Enum):
    """Supported agent types."""
    DOCUMENT = "document"
    IDENTITY = "identity"
    AML = "aml"
    ADVERSE_MEDIA = "adverse_media"
    COMPLIANCE = "compliance"
    RISK = "risk"
    AUDIT = "audit"


@dataclass
class AgentContext:
    """Context passed between agents."""
    case_id: str
    customer_id: str
    correlation_id: str
    metadata: dict[str, Any]
    timestamp: datetime


@dataclass
class AgentResult:
    """Result from agent execution."""
    agent_type: AgentType
    status: AgentStatus
    score: Optional[float] = None
    data: Optional[dict[str, Any]] = None
    errors: Optional[list[str]] = None
    next_agent: Optional[AgentType] = None
    requires_review: bool = False
    timestamp: datetime = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "score": self.score,
            "data": self.data,
            "errors": self.errors,
            "next_agent": self.next_agent.value if self.next_agent else None,
            "requires_review": self.requires_review,
            "timestamp": self.timestamp.isoformat()
        }


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, agent_type: AgentType, config: Optional[dict[str, Any]] = None):
        self.agent_type = agent_type
        self.config = config or {}
        self.status = AgentStatus.IDLE

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute agent logic."""
        pass

    @abstractmethod
    def validate(self, context: AgentContext) -> bool:
        """Validate input context."""
        pass

    @abstractmethod
    def get_required_tools(self) -> list[str]:
        """Return list of required tool names."""
        pass

    def set_status(self, status: AgentStatus) -> None:
        """Update agent status."""
        self.status = status

    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return self.status