"""Identity Verification Agent Tests."""

import pytest
from datetime import datetime

from app.agents.identity_verification_agent import (
    IdentityVerificationAgent,
    IdentityMatchLevel,
    DuplicateRisk
)
from app.agents.base import AgentContext, AgentType, AgentStatus


@pytest.mark.asyncio
async def test_identity_verification_high_confidence():
    """Test identity verification with high confidence match."""
    agent = IdentityVerificationAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Smith",
            "date_of_birth": "1985-05-15",
            "document_numbers": ["A1234567", "DL-01-12345678"],
            "documents": [
                {"type": "passport", "extracted_name": "John Smith"},
                {"type": "driving_license", "extracted_name": "Smith, John"}
            ]
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.IDENTITY
    assert result.status == AgentStatus.COMPLETED
    assert result.score >= 0.7
    assert result.data["verified"] is True


@pytest.mark.asyncio
async def test_identity_verification_low_confidence():
    """Test identity verification with low confidence."""
    agent = IdentityVerificationAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Smith",
            "date_of_birth": "1985-05-15",
            "document_numbers": ["A1234567"],
            "documents": [
                {"type": "passport", "extracted_name": "Different Name"}
            ]
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.IDENTITY
    assert result.score < 0.7


@pytest.mark.asyncio
async def test_duplicate_detection():
    """Test duplicate identity detection."""
    agent = IdentityVerificationAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Doe",
            "date_of_birth": "1990-01-01",
            "document_numbers": ["A001", "A002"]
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.data["duplicate_risk"] in [DuplicateRisk.LOW.value, DuplicateRisk.MEDIUM.value, DuplicateRisk.HIGH.value]


@pytest.mark.asyncio
async def test_synthetic_identity_detection():
    """Test synthetic identity pattern detection."""
    agent = IdentityVerificationAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Doe",  # Generic name
            "date_of_birth": "1900-01-01",  # Suspicious DOB
            "document_numbers": [],
            "documents": []
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.data["synthetic_risk"] > 0.0


@pytest.mark.asyncio
async def test_cross_document_validation():
    """Test cross-document validation."""
    agent = IdentityVerificationAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Smith",
            "date_of_birth": "1985-05-15",
            "documents": [
                {"type": "passport", "date_of_birth": "1985-05-15"},
                {"type": "driving_license", "date_of_birth": "1985-06-15"}  # Different DOB
            ]
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert len(result.data["cross_doc_issues"]) > 0


@pytest.mark.asyncio
async def test_requires_review_when_low_confidence():
    """Test that low confidence triggers review flag."""
    agent = IdentityVerificationAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={
            "full_name": "John Smith",
            "date_of_birth": "1985-05-15",
            "documents": [
                {"type": "passport", "extracted_name": "Different Person"}
            ]
        },
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.requires_review is True


def test_match_level_conversion():
    """Test match level to score conversion."""
    agent = IdentityVerificationAgent()

    assert agent._match_level_to_score("high") == 1.0
    assert agent._match_level_to_score("medium") == 0.7
    assert agent._match_level_to_score("low") == 0.4
    assert agent._match_level_to_score("no_match") == 0.0


def test_name_variant_generation():
    """Test name variant generation."""
    agent = IdentityVerificationAgent()

    variants = agent._generate_name_variants("John Smith")
    assert "john smith" in variants
    assert any("smith" in v for v in variants)


def test_sequential_number_detection():
    """Test sequential document number detection."""
    agent = IdentityVerificationAgent()

    assert agent._is_sequential(["A001", "A002"]) is True
    assert agent._is_sequential(["A001", "A003"]) is False
    assert agent._is_sequential([]) is False


def test_suspicious_dob_detection():
    """Test suspicious date of birth detection."""
    agent = IdentityVerificationAgent()

    assert agent._is_suspicious_dob("1900-01-01") is True
    assert agent._is_suspicious_dob("1990-05-15") is False