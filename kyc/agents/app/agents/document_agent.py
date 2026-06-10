"""Document Agent - handles document validation and OCR."""

import logging
from typing import Any, Optional

from app.agents.base import BaseAgent, AgentType, AgentContext, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class DocumentAgent(BaseAgent):
    """Agent for document validation and OCR extraction."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(AgentType.DOCUMENT, config)

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute document processing."""
        self.set_status(AgentStatus.RUNNING)

        if not self.validate(context):
            self.set_status(AgentStatus.FAILED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                errors=["Invalid context: no document data provided"]
            )

        try:
            # Mock document processing
            documents = context.metadata.get("documents", [])
            processed_count = len(documents)
            score = min(100, processed_count * 20)  # Simple scoring

            confidence_scores = [doc.get("confidence", 0.8) for doc in documents]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5

            self.set_status(AgentStatus.COMPLETED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                score=score,
                data={
                    "processed_documents": processed_count,
                    "avg_confidence": avg_confidence,
                    "extracted_data": context.metadata.get("documents", [])
                },
                next_agent=AgentType.IDENTITY
            )
        except Exception as e:
            logger.error(f"Document agent failed", exc_info=True)
            self.set_status(AgentStatus.FAILED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                errors=[str(e)]
            )

    def validate(self, context: AgentContext) -> bool:
        """Validate input context has document data."""
        return "documents" in context.metadata or context.metadata.get("skip_documents", False)

    def get_required_tools(self) -> list[str]:
        return ["ocr_tool", "document_validator", "metadata_extractor"]