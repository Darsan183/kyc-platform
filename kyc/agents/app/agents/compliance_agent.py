"""Compliance Agent - handles regulatory compliance checks."""

import logging
from typing import Any, Optional

from app.agents.base import BaseAgent, AgentType, AgentContext, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class ComplianceAgent(BaseAgent):
    """Agent for regulatory compliance verification."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(AgentType.COMPLIANCE, config)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute compliance checks."""
        self.set_status(AgentStatus.RUNNING)

        try:
            # Mock compliance check
            jurisdiction = context.metadata.get("country", "US")
            rules = context.metadata.get("compliance_rules", {})

            violations = rules.get("violations", [])

            score = 100 if len(violations) == 0 else max(0, 100 - (len(violations) * 30))

            self.set_status(AgentStatus.COMPLETED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                score=score,
                data={
                    "jurisdiction": jurisdiction,
                    "violations": violations,
                    "compliant": len(violations) == 0
                },
                next_agent=AgentType.RISK,
                requires_review=len(violations) > 0
            )
        except Exception as e:
            logger.error(f"Compliance agent failed", exc_info=True)
            self.set_status(AgentStatus.FAILED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                errors=[str(e)]
            )

    def validate(self, context: AgentContext) -> bool:
        """Validate input context has customer data."""
        return "customer_data" in context.metadata or "full_name" in context.metadata

    def get_required_tools(self) -> list[str]:
        return ["rule_engine", "regulation_checker", "jurisdiction_mapper"]