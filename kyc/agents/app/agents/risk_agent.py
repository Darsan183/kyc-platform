"""Risk Agent - handles risk scoring and assessment."""

import logging
from typing import Any, Optional

from app.agents.base import BaseAgent, AgentType, AgentContext, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class RiskAgent(BaseAgent):
    """Agent for risk assessment and scoring."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(AgentType.RISK, config)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute risk assessment."""
        self.set_status(AgentStatus.RUNNING)

        try:
            # Aggregate scores from previous agents
            # Weights: Document(25%), Identity(20%), AML(25%), Media(20%), Compliance(10%)
            scores = context.metadata.get("scores", {})

            document_score = scores.get("document", 100)
            identity_score = scores.get("identity", 100)
            aml_score = scores.get("aml", 100)
            media_score = scores.get("media", 100)
            compliance_score = scores.get("compliance", 100)

            weighted_score = (
                document_score * 0.25 +
                identity_score * 0.20 +
                aml_score * 0.25 +
                media_score * 0.20 +
                compliance_score * 0.10
            )

            # Determine risk level
            if weighted_score >= 80:
                risk_level = "LOW"
            elif weighted_score >= 60:
                risk_level = "MEDIUM"
            elif weighted_score >= 40:
                risk_level = "HIGH"
            else:
                risk_level = "CRITICAL"

            self.set_status(AgentStatus.COMPLETED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                score=weighted_score,
                data={
                    "risk_level": risk_level,
                    "component_scores": scores,
                    "factors": {
                        "document_weight": 0.25,
                        "identity_weight": 0.20,
                        "aml_weight": 0.25,
                        "media_weight": 0.20,
                        "compliance_weight": 0.10
                    }
                },
                next_agent=AgentType.AUDIT,
                requires_review=risk_level in ["HIGH", "CRITICAL"]
            )
        except Exception as e:
            logger.error(f"Risk agent failed", exc_info=True)
            self.set_status(AgentStatus.FAILED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                errors=[str(e)]
            )

    def validate(self, context: AgentContext) -> bool:
        """Validate input context has scores."""
        return "scores" in context.metadata or "customer_data" in context.metadata

    def get_required_tools(self) -> list[str]:
        return ["risk_calculator", "explanation_generator", "threshold_checker"]