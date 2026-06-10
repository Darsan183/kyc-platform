"""Risk Scoring Tests."""

import pytest
from datetime import datetime

from app.agents.base import AgentType, AgentStatus
from app.agents.risk_scoring_engine import RiskScoringEngine, RiskLevel


@pytest.mark.asyncio
async def test_risk_scoring_low_risk():
    """Test risk scoring with low risk inputs."""
    agent = RiskScoringEngine()

    context = type('obj', (object,), {
        'case_id': 'test-case-001',
        'customer_id': 'test-customer-001',
        'correlation_id': 'test-correlation-001',
        'metadata': {
            "identity_score": 95,
            "document_score": 100,
            "aml_hits": 0,
            "aml_risk_level": "low",
            "media_negative_articles": 0,
            "media_total_articles": 0,
            "compliance_violations": 0
        },
        'timestamp': datetime.utcnow()
    })()

    result = await agent.execute(context)

    assert result.agent_type == AgentType.RISK
    assert result.status == AgentStatus.COMPLETED
    assert result.data["risk_level"] == "low"


@pytest.mark.asyncio
async def test_risk_scoring_high_risk():
    """Test risk scoring with high risk inputs."""
    agent = RiskScoringEngine()

    context = type('obj', (object,), {
        'case_id': 'test-case-001',
        'customer_id': 'test-customer-001',
        'correlation_id': 'test-correlation-001',
        'metadata': {
            "identity_score": 40,
            "document_score": 50,
            "aml_hits": 2,
            "aml_risk_level": "high",
            "media_negative_articles": 3,
            "media_total_articles": 5,
            "compliance_violations": 1
        },
        'timestamp': datetime.utcnow()
    })()

    result = await agent.execute(context)

    assert result.status == AgentStatus.COMPLETED
    assert result.data["risk_level"] in ["medium", "high", "critical"]


@pytest.mark.asyncio
async def test_risk_scoring_critical_risk():
    """Test risk scoring with critical risk inputs."""
    agent = RiskScoringEngine()

    context = type('obj', (object,), {
        'case_id': 'test-case-001',
        'customer_id': 'test-customer-001',
        'correlation_id': 'test-correlation-001',
        'metadata': {
            "identity_score": 20,
            "document_score": 30,
            "aml_hits": 5,
            "aml_risk_level": "critical",
            "media_negative_articles": 10,
            "media_total_articles": 10,
            "compliance_violations": 3
        },
        'timestamp': datetime.utcnow()
    })()

    result = await agent.execute(context)

    assert result.data["risk_level"] == "critical"
    assert result.data["decision"] == "REJECT"


def test_weighted_aggregation():
    """Test weighted score aggregation."""
    agent = RiskScoringEngine()

    scores = {
        "identity_score": 90,
        "document_score": 80,
        "aml_hits": 0,
        "aml_risk_level": "low",
        "media_negative_articles": 1,
        "media_total_articles": 5,
        "compliance_violations": 0
    }

    normalized = agent._normalize_scores(scores)

    assert "normalized_scores" in normalized
    assert normalized["normalized_scores"]["identity"] == 90
    assert normalized["normalized_scores"]["aml"] == 100  # low risk


def test_risk_level_assignment():
    """Test risk level thresholds."""
    agent = RiskScoringEngine()

    state_low = {"ml_adjusted_score": 85}
    assert agent._assign_risk_level(state_low)["risk_level"] == RiskLevel.LOW

    state_medium = {"ml_adjusted_score": 65}
    assert agent._assign_risk_level(state_medium)["risk_level"] == RiskLevel.MEDIUM

    state_high = {"ml_adjusted_score": 50}
    assert agent._assign_risk_level(state_high)["risk_level"] == RiskLevel.HIGH

    state_critical = {"ml_adjusted_score": 25}
    assert agent._assign_risk_level(state_critical)["risk_level"] == RiskLevel.CRITICAL


def test_decision_engine():
    """Test decision logic."""
    agent = RiskScoringEngine()

    assert agent._get_decision_text(RiskLevel.LOW) == "APPROVE - No additional review required"
    assert agent._get_decision_text(RiskLevel.MEDIUM) == "MONITOR - Ongoing monitoring recommended"
    assert agent._get_decision_text(RiskLevel.HIGH) == "ENHANCED_REVIEW - Enhanced due diligence required"
    assert agent._get_decision_text(RiskLevel.CRITICAL) == "REJECT - Applicant should be rejected"


def test_custom_weights():
    """Test custom weight configuration."""
    custom_weights = {
        "identity": 0.30,
        "document": 0.30,
        "aml": 0.20,
        "media": 0.10,
        "compliance": 0.10
    }

    agent = RiskScoringEngine(config={"weights": custom_weights})

    assert agent.weights["identity"] == 0.30
    assert agent.weights["document"] == 0.30


def test_confidence_calculation():
    """Test confidence score calculation."""
    agent = RiskScoringEngine()

    state = {"normalized_scores": {"identity": 90, "document": 80, "aml": 100}}
    confidence = agent._calculate_confidence(state)

    assert 0.0 <= confidence <= 1.0
    assert confidence > 0.8  # High scores should yield high confidence


@pytest.mark.asyncio
async def test_evidence_collection():
    """Test evidence collection."""
    agent = RiskScoringEngine()

    context = type('obj', (object,), {
        'case_id': 'test-case-001',
        'customer_id': 'test-customer-001',
        'correlation_id': 'test-correlation-001',
        'metadata': {"identity_score": 100},
        'timestamp': datetime.utcnow()
    })()

    result = await agent.execute(context)

    assert "evidence" in result.data
    assert "thresholds_used" in result.data["evidence"]


@pytest.mark.asyncio
async def test_explanation_generation():
    """Test explanation generation."""
    agent = RiskScoringEngine()

    context = type('obj', (object,), {
        'case_id': 'test-case-001',
        'customer_id': 'test-customer-001',
        'correlation_id': 'test-correlation-001',
        'metadata': {"identity_score": 100},
        'timestamp': datetime.utcnow()
    })()

    result = await agent.execute(context)

    assert "explanation" in result.data
    assert len(result.data["explanation"]) > 0


def test_component_serialization():
    """Test risk component serialization."""
    from app.agents.risk_scoring_engine import RiskComponent

    component = RiskComponent(
        name="aml",
        score=75.0,
        weight=0.25,
        evidence={"hits": 2},
        reasons=["Sanctions hit detected"]
    )

    agent = RiskScoringEngine()
    result = agent._component_to_dict(component)

    assert result["name"] == "aml"
    assert result["score"] == 75.0


@pytest.mark.asyncio
async def test_requires_review_flag():
    """Test review flag based on risk level."""
    agent = RiskScoringEngine()

    low_risk_context = type('obj', (object,), {
        'case_id': 'test-case-001',
        'customer_id': 'test-customer-001',
        'correlation_id': 'test-correlation-001',
        'metadata': {
            "identity_score": 100,
            "document_score": 100,
            "aml_risk_level": "low"
        },
        'timestamp': datetime.utcnow()
    })()

    low_result = await agent.execute(low_risk_context)
    assert low_result.requires_review is False
    assert low_result.data["risk_level"] == "low"