"""Adverse Media Agent - handles negative media analysis."""

import logging
from typing import Any, Optional

from app.agents.base import BaseAgent, AgentType, AgentContext, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class MediaAgent(BaseAgent):
    """Agent for adverse media screening."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(AgentType.ADVERSE_MEDIA, config)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute adverse media analysis."""
        self.set_status(AgentStatus.RUNNING)

        try:
            # Mock media analysis
            customer_name = context.metadata.get("full_name", "")
            media_result = context.metadata.get("media_analysis", {})

            articles = media_result.get("articles", [])
            negative_count = sum(1 for a in articles if a.get("sentiment") == "negative")

            # Score based on negative articles
            score = max(0, 100 - (negative_count * 15))
            requires_review = negative_count > 2

            self.set_status(AgentStatus.COMPLETED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                score=score,
                data={
                    "articles_analyzed": len(articles),
                    "negative_articles": negative_count,
                    "sentiment_score": media_result.get("avg_sentiment", 0.5)
                },
                next_agent=AgentType.COMPLIANCE,
                requires_review=requires_review
            )
        except Exception as e:
            logger.error(f"Media agent failed", exc_info=True)
            self.set_status(AgentStatus.FAILED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                errors=[str(e)]
            )

    def validate(self, context: AgentContext) -> bool:
        """Validate input context has customer data."""
        return "full_name" in context.metadata

    def get_required_tools(self) -> list[str]:
        return ["news_aggregator", "sentiment_analyzer", "entity_resolver"]