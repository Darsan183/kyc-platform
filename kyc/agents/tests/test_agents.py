"""Agent Unit Tests."""

import pytest
from datetime import datetime

from app.agents.base import AgentStatus, AgentContext, AgentType
from app.agents.document_agent import DocumentAgent
from app.agents.identity_agent import IdentityAgent
from app.agents.aml_agent import AmlAgent
from app.agents.media_agent import MediaAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.risk_agent import RiskAgent
from app.agents.audit_agent import AuditAgent


@pytest.mark.asyncio
async def test_document_agent_execution(sample_customer_data):
    """Test document agent processes correctly."""
    agent = DocumentAgent()
    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata=sample_customer_data,
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.DOCUMENT
    assert result.status == AgentStatus.COMPLETED
    assert result.score is not None
    assert "processed_documents" in result.data


@pytest.mark.asyncio
async def test_identity_agent_execution():
    """Test identity agent processes correctly."""
    agent = IdentityAgent()
    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={"full_name": "John Doe", "identity": {"confidence": 0.9}},
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.IDENTITY
    assert result.status == AgentStatus.COMPLETED


@pytest.mark.asyncio
async def test_aml_agent_execution():
    """Test AML agent processes correctly."""
    agent = AmlAgent()
    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={"full_name": "John Doe", "aml_screening": {"hits": []}},
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.AML
    assert result.status == AgentStatus.COMPLETED
    assert result.data["hit_count"] == 0


@pytest.mark.asyncio
async def test_media_agent_execution():
    """Test media agent processes correctly."""
    agent = MediaAgent()
    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={"full_name": "John Doe", "media_analysis": {"articles": []}},
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.ADVERSE_MEDIA
    assert result.status == AgentStatus.COMPLETED


@pytest.mark.asyncio
async def test_compliance_agent_execution():
    """Test compliance agent processes correctly."""
    agent = ComplianceAgent()
    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={"customer_data": {}, "country": "US"},
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.COMPLIANCE
    assert result.status == AgentStatus.COMPLETED


@pytest.mark.asyncio
async def test_risk_agent_execution(sample_customer_data):
    """Test risk agent calculates score correctly."""
    agent = RiskAgent()
    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata=sample_customer_data,
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.RISK
    assert result.status == AgentStatus.COMPLETED
    assert result.score is not None
    assert result.data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


@pytest.mark.asyncio
async def test_audit_agent_execution():
    """Test audit agent generates audit trail."""
    agent = AuditAgent()
    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={"final_risk_score": 85},
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.AUDIT
    assert result.status == AgentStatus.COMPLETED
    assert result.data["final_decision"] == "APPROVE"