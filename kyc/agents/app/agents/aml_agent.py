"""AML Agent - handles sanctions and watchlist screening."""

import logging
from typing import Any, Optional

from app.agents.base import BaseAgent, AgentType, AgentContext, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class AmlAgent(BaseAgent):
    """Agent for AML screening against sanctions and watchlists."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(AgentType.AML, config)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute AML screening."""
        self.set_status(AgentStatus.RUNNING)

        try:
            # Mock AML screening
            customer_name = context.metadata.get("full_name", "")
            screening_result = context.metadata.get("aml_screening", {})

            hits = screening_result.get("hits", [])
            hit_count = len(hits)

            # Score based on no hits
            score = max(0, 100 - (hit_count * 20))
            requires_review = hit_count > 0

            self.set_status(AgentStatus.COMPLETED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                score=score,
                data={
                    "screened": True,
                    "hit_count": hit_count,
                    "hits": hits
                },
                next_agent=AgentType.ADVERSE_MEDIA,
                requires_review=requires_review
            )
        except Exception as e:
            logger.error(f"AML agent failed", exc_info=True)
            self.set_status(AgentStatus.FAILED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                errors=[str(e)]
            )

    def validate(self, context: AgentContext) -> bool:
        """Validate input context has customer data."""
        return "full_name" in context.metadata or "customer_data" in context.metadata

    def get_required_tools(self) -> list[str]:
        return ["sanctions_screener", "pep_detector", "watchlist_matcher"]