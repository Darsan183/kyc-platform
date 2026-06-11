"""Workflow Engine - manages agent workflow execution."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional, Callable

from app.models.state import CaseState
from app.agents.base import AgentType, AgentStatus, AgentContext, AgentResult

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Manages workflow execution and state transitions."""

    def __init__(self):
        self.workflow_registry: dict[str, Callable] = {}
        self.state_store: dict[str, CaseState] = {}

    async def execute_workflow(
        self,
        workflow_name: str,
        state: CaseState,
        executor: Any
    ) -> CaseState:
        """Execute a workflow by name."""
        workflow = self.workflow_registry.get(workflow_name)
        if not workflow:
            state.add_error(f"Workflow not found: {workflow_name}")
            return state

        try:
            state = await workflow(state, executor)
            state.status = AgentStatus.COMPLETED
            state.completed_at = datetime.utcnow()
        except Exception as e:
            state.add_error(f"Workflow execution failed: {str(e)}")
            state.status = AgentStatus.FAILED
            logger.error(f"Workflow {workflow_name} failed", exc_info=True)

        return state

    def register_workflow(self, name: str, workflow: Callable) -> None:
        """Register a workflow."""
        self.workflow_registry[name] = workflow


# Default workflow engine instance
workflow_engine = WorkflowEngine()