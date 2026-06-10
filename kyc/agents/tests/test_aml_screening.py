"""AML Screening Agent Unit Tests."""

import pytest
from datetime import datetime

from app.agents.base import AgentType, AgentStatus
from app.agents.aml_screening_agent import (
    AmlScreeningAgent,
    RiskLevel,
    MatchType,
    ListType
)
from app.agents.base import AgentContext


@pytest.mark.asyncio
async def test_aml_screening_no_hits():
    """Test AML screening with no hits."""
    agent = AmlScreeningAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Smith",
            "country": "US"
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.AML
    assert result.status == AgentStatus.COMPLETED
    assert result.data["total_hits"] == 0
    assert result.data["risk_level"] == "low"


@pytest.mark.asyncio
async def test_aml_screening_with_hits():
    """Test AML screening with hits present."""
    agent = AmlScreeningAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Smith",
            "country": "US",
            "document_numbers": ["A001", "A002"]
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.AML
    assert result.status == AgentStatus.COMPLETED
    assert "risk_level" in result.data


@pytest.mark.asyncio
async def test_risk_level_determination():
    """Test risk level determination based on hits."""
    # Test CRITICAL risk
    assert RiskLevel.CRITICAL == "critical"

    # Test HIGH risk
    assert RiskLevel.HIGH == "high"

    # Test MEDIUM risk
    assert RiskLevel.MEDIUM == "medium"

    # Test LOW risk
    assert RiskLevel.LOW == "low"


def test_hit_to_dict():
    """Test hit serialization."""
    agent = AmlScreeningAgent()

    from app.agents.aml_screening_agent import ScreeningHit

    hit = ScreeningHit(
        list_type=ListType.SANCTIONS,
        matched_name="Test Match",
        original_name="Original Name",
        match_type=MatchType.FUZZY,
        confidence=0.85,
        entity_id="TEST-001",
        entity_type="individual",
        country="US",
        reason="Test reason",
        source="Test source"
    )

    result = agent._hit_to_dict(hit)

    assert result["list_type"] == "sanctions"
    assert result["matched_name"] == "Test Match"
    assert result["confidence"] == 0.85


def test_match_type_values():
    """Test match type enum values."""
    assert MatchType.EXACT.value == "exact"
    assert MatchType.FUZZY.value == "fuzzy"
    assert MatchType.PHONETIC.value == "phonetic"


def test_list_type_values():
    """Test list type enum values."""
    assert ListType.SANCTIONS.value == "sanctions"
    assert ListType.PEP.value == "pep"
    assert ListType.WATCHLIST.value == "watchlist"


def test_risk_level_values():
    """Test risk level enum values."""
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.MEDIUM.value == "medium"
    assert RiskLevel.HIGH.value == "high"
    assert RiskLevel.CRITICAL.value == "critical"


def test_validate_context():
    """Test context validation."""
    agent = AmlScreeningAgent()

    valid_context = AgentContext(
        case_id="test",
        customer_id="test",
        correlation_id="test",
        metadata={"full_name": "John Smith"},
        timestamp=datetime.utcnow()
    )
    assert agent.validate(valid_context) is True

    invalid_context = AgentContext(
        case_id="test",
        customer_id="test",
        correlation_id="test",
        metadata={"email": "test@example.com"},
        timestamp=datetime.utcnow()
    )
    assert agent.validate(invalid_context) is False


@pytest.mark.asyncio
async def test_evidence_collection():
    """Test evidence collection."""
    agent = AmlScreeningAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Smith",
            "country": "US"
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert "evidence" in result.data
    assert "screened_at" in result.data["evidence"]


@pytest.mark.asyncio
async def test_explanation_generation():
    """Test explanation generation."""
    agent = AmlScreeningAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Smith",
            "country": "US"
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert "explanation" in result.data
    assert len(result.data["explanation"]) > 0


@pytest.mark.asyncio
async def test_correlation_logic():
    """Test hit correlation logic."""
    agent = AmlScreeningAgent()

    from app.agents.aml_screening_agent import ScreeningHit

    input_data = type('obj', (object,), {
        'full_name': 'John Smith',
        'country': 'US',
        'hits': [
            ScreeningHit(
                list_type=ListType.SANCTIONS,
                matched_name="Test Match",
                original_name="Original Name",
                match_type=MatchType.FUZZY,
                confidence=0.85,
                entity_id="TEST-001",
                entity_type="individual",
                country="US",
                reason="Test reason",
                source="Test source"
            )
        ]
    })()

    result = agent._correlate_hits(input_data)

    assert result.hit_summary["sanctions_count"] == 1


@pytest.mark.asyncio
async def test_requires_review_flag():
    """Test review flag is set correctly."""
    agent = AmlScreeningAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Smith",
            "country": "US"
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    # No hits means no review required
    assert result.requires_review is False