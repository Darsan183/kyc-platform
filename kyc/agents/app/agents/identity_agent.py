"""Identity Agent - handles identity verification."""

import logging
from typing import Any, Optional

from app.agents.base import BaseAgent, AgentType, AgentContext, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class IdentityAgent(BaseAgent):
    """Agent for identity verification and biometric matching."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(AgentType.IDENTITY, config)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute identity verification."""
        self.set_status(AgentStatus.RUNNING)

        try:
            # Mock identity verification
            identity_data = context.metadata.get("identity", {})
            matches = identity_data.get("matches", 0)
            confidence = identity_data.get("confidence", 0.0)

            score = int(confidence * 100)

            # Check if requires manual review
            requires_review = confidence < 0.8 or matches == 0

            self.set_status(AgentStatus.COMPLETED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                score=score,
                data={
                    "verified": confidence >= 0.7,
                    "confidence": confidence,
                    "matches_found": matches
                },
                next_agent=AgentType.AML,
                requires_review=requires_review
            )
        except Exception as e:
            logger.error(f"Identity agent failed", exc_info=True)
            self.set_status(AgentStatus.FAILED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                errors=[str(e)]
            )

    def validate(self, context: AgentContext) -> bool:
        """Validate input context has identity data."""
        return "identity" in context.metadata or context.metadata.get("skip_identity", False)

    def get_required_tools(self) -> list[str]:
        return ["biometric_matcher", "liveness_detector", "database_verifier"]