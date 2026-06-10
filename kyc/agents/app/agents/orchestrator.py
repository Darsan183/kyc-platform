"""Agent Orchestrator - Central coordination for AI agents."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

import redis
import json
from langgraph.graph import StateGraph, END

from app.agents.base import AgentType, AgentStatus, AgentContext, AgentResult
from app.agents.document_agent import DocumentAgent
from app.agents.identity_agent import IdentityAgent
from app.agents.aml_agent import AmlAgent
from app.agents.media_agent import MediaAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.risk_agent import RiskAgent
from app.agents.audit_agent import AuditAgent
from app.models.state import CaseState


logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates agent execution and workflow management with Redis-backed state."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.agents = self._initialize_agents()
        self.redis_client = self._init_redis()
        
        # Build conditional workflow
        self.workflow = self._build_workflow()

    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for distributed state."""
        try:
            redis_url = self.config.get("redis_url", "redis://localhost:6379")
            return redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis not available for state persistence: {e}")
            return None

    def _initialize_agents(self) -> dict[AgentType, Any]:
        """Initialize all agents."""
        return {
            AgentType.DOCUMENT: DocumentAgent(),
            AgentType.IDENTITY: IdentityAgent(),
            AgentType.AML: AmlAgent(),
            AgentType.ADVERSE_MEDIA: MediaAgent(),
            AgentType.COMPLIANCE: ComplianceAgent(),
            AgentType.RISK: RiskAgent(),
            AgentType.AUDIT: AuditAgent(),
        }

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with conditional routing."""
        workflow = StateGraph(CaseState)

        # Add nodes for each agent
        workflow.add_node("document", self._run_document_agent)
        workflow.add_node("identity", self._run_identity_agent)
        workflow.add_node("aml", self._run_aml_agent)
        workflow.add_node("media", self._run_media_agent)
        workflow.add_node("compliance", self._run_compliance_agent)
        workflow.add_node("risk", self._run_risk_agent)
        workflow.add_node("audit", self._run_audit_agent)

        # Define conditional edges for retry logic
        workflow.set_entry_point("document")
        workflow.add_edge("document", "identity")
        workflow.add_edge("identity", "aml")
        workflow.add_edge("aml", "media")
        workflow.add_edge("media", "compliance")
        workflow.add_edge("compliance", "risk")
        workflow.add_conditional_edges("risk", self._route_after_risk)
        workflow.add_edge("audit", END)

        return workflow.compile()

    def _route_after_risk(self, state: CaseState) -> str:
        """Route to audit or require review based on risk level."""
        risk_result = state.risk_result
        if risk_result and risk_result.requires_review:
            # For review, still proceed to audit but flag for attention
            state.workflow_data["requires_human_review"] = True
        return "audit"

    async def process_case(self, case_id: str, customer_id: str, customer_data: dict[str, Any]) -> CaseState:
        """Process a KYC case through all agents with state persistence."""
        initial_state = CaseState(
            case_id=case_id,
            customer_id=customer_id,
            customer_data=customer_data
        )

        # Store initial state in Redis
        self._persist_state(initial_state)

        context = AgentContext(
            case_id=case_id,
            customer_id=customer_id,
            correlation_id=initial_state.correlation_id,
            metadata=customer_data,
            timestamp=datetime.utcnow()
        )

        current_state = initial_state

        # Execute workflow with retry support
        for attempt in range(3):  # Retry up to 3 times
            try:
                current_state = await self._execute_workflow(context, current_state, attempt)
                if current_state.status != AgentStatus.FAILED:
                    break
            except Exception as e:
                logger.error(f"Workflow attempt {attempt + 1} failed", exc_info=True)
                if attempt == 2:
                    current_state.add_error(f"Workflow failed after 3 attempts: {e}")

        self._persist_state(current_state)
        return current_state

    async def _execute_workflow(self, context: AgentContext, state: CaseState, attempt: int) -> CaseState:
        """Execute agent workflow."""
        for agent_type in [
            AgentType.DOCUMENT, AgentType.IDENTITY, AgentType.AML,
            AgentType.ADVERSE_MEDIA, AgentType.COMPLIANCE, AgentType.RISK, AgentType.AUDIT
        ]:
            try:
                agent = self.agents[agent_type]
                result = await agent.execute(context)
                state.set_result(result)
                state.current_agent = agent_type
                state.status = result.status

                if result.status == AgentStatus.FAILED:
                    state.add_error(f"Agent {agent_type} failed: {result.errors}")
                    # Don't break - continue to audit to record failure

                self._persist_state(state)

            except Exception as e:
                logger.error(f"Agent {agent_type} execution failed", exc_info=True)
                state.add_error(str(e))

        return state

    def _persist_state(self, state: CaseState) -> None:
        """Persist workflow state to Redis for distributed recovery."""
        if self.redis_client:
            try:
                key = f"kyc:workflow:{state.case_id}"
                self.redis_client.setex(key, 86400, json.dumps(state.to_dict()))  # 24h TTL
            except Exception as e:
                logger.debug(f"Could not persist state: {e}")

    async def get_persisted_state(self, case_id: str) -> Optional[CaseState]:
        """Retrieve persisted workflow state."""
        if self.redis_client:
            try:
                key = f"kyc:workflow:{case_id}"
                data = self.redis_client.get(key)
                if data:
                    return CaseState(**json.loads(data))
            except Exception as e:
                logger.debug(f"Could not retrieve state: {e}")
        return None

    async def _run_document_agent(self, state: CaseState) -> dict:
        return await self._run_agent_node(state, AgentType.DOCUMENT, 0.14)

    async def _run_identity_agent(self, state: CaseState) -> dict:
        return await self._run_agent_node(state, AgentType.IDENTITY, 0.28)

    async def _run_aml_agent(self, state: CaseState) -> dict:
        return await self._run_agent_node(state, AgentType.AML, 0.42)

    async def _run_media_agent(self, state: CaseState) -> dict:
        return await self._run_agent_node(state, AgentType.ADVERSE_MEDIA, 0.56)

    async def _run_compliance_agent(self, state: CaseState) -> dict:
        return await self._run_agent_node(state, AgentType.COMPLIANCE, 0.70)

    async def _run_agent_node(self, state: CaseState, agent_type: AgentType, progress: float) -> dict:
        """Generic agent node runner."""
        context = AgentContext(
            case_id=state.case_id,
            customer_id=state.customer_id,
            correlation_id=state.correlation_id,
            metadata=state.customer_data,
            timestamp=datetime.utcnow()
        )
        result = await self.agents[agent_type].execute(context)
        state.set_result(result)
        state.current_agent = agent_type
        self._persist_state(state)
        return {"progress": progress}

    async def _run_risk_agent(self, state: CaseState) -> dict:
        """Run risk agent node."""
        context = AgentContext(
            case_id=state.case_id,
            customer_id=state.customer_id,
            correlation_id=state.correlation_id,
            metadata=state.customer_data,
            timestamp=datetime.utcnow()
        )
        result = await self.agents[AgentType.RISK].execute(context)
        state.set_result(result)
        state.final_risk_score = result.score
        state.current_agent = AgentType.RISK
        self._persist_state(state)
        return {"progress": 0.85}

    async def _run_audit_agent(self, state: CaseState) -> dict:
        """Run audit agent node."""
        context = AgentContext(
            case_id=state.case_id,
            customer_id=state.customer_id,
            correlation_id=state.correlation_id,
            metadata=state.customer_data,
            timestamp=datetime.utcnow()
        )
        result = await self.agents[AgentType.AUDIT].execute(context)
        state.set_result(result)
        state.completed_at = datetime.utcnow()
        self._persist_state(state)
        return {"progress": 1.0}