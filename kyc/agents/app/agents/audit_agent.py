"""Audit Agent - handles audit trail generation."""

import logging
from typing import Any, Optional

from app.agents.base import BaseAgent, AgentType, AgentContext, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class AuditAgent(BaseAgent):
    """Agent for audit trail generation."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(AgentType.AUDIT, config)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Generate audit trail."""
        self.set_status(AgentStatus.RUNNING)

        try:
            # Collect all results for audit
            audit_data = {
                "case_id": context.case_id,
                "customer_id": context.customer_id,
                "correlation_id": context.correlation_id,
                "agents_executed": [],
                "events": []
            }

            # Mock audit trail creation
            audit_data["agents_executed"] = context.metadata.get("executed_agents", [
                "document", "identity", "aml", "media", "compliance", "risk"
            ])

            audit_data["events"].append({
                "type": "case_processed",
                "timestamp": context.timestamp.isoformat()
            })

            # Determine final decision based on risk score
            risk_score = context.metadata.get("final_risk_score", 50)
            if risk_score >= 70:
                decision = "APPROVE"
            elif risk_score >= 40:
                decision = "REVIEW"
            else:
                decision = "ESCALATE"

            audit_data["final_decision"] = decision

            self.set_status(AgentStatus.COMPLETED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                score=100.0,
                data=audit_data,
                next_agent=None
            )
        except Exception as e:
            logger.error(f"Audit agent failed", exc_info=True)
            self.set_status(AgentStatus.FAILED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                errors=[str(e)]
            )

    def validate(self, context: AgentContext) -> bool:
        """Validate input context."""
        return context.metadata is not None

    def get_required_tools(self) -> list[str]:
        return ["audit_logger", "evidence_collector", "report_generator"]