"""Adverse Media Agent Tests."""

import pytest
from datetime import datetime

from app.agents.base import AgentType, AgentStatus
from app.agents.adverse_media_agent import (
    AdverseMediaAgent,
    MediaRisk,
    Sentiment,
    SourceType,
    MediaArticle
)
from app.agents.base import AgentContext


@pytest.mark.asyncio
async def test_adverse_media_screening_no_articles():
    """Test adverse media screening with no articles."""
    agent = AdverseMediaAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={"full_name": "John Smith"},
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.ADVERSE_MEDIA
    assert result.status == AgentStatus.COMPLETED
    assert result.data["risk_level"] == "low"


@pytest.mark.asyncio
async def test_adverse_media_with_articles():
    """Test adverse media screening with articles."""
    agent = AdverseMediaAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={"full_name": "John Smith", "aliases": ["J Smith"]},
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert result.agent_type == AgentType.ADVERSE_MEDIA
    assert "total_articles" in result.data
    assert "negative_articles" in result.data


def test_sentiment_classification():
    """Test sentiment mock classification."""
    agent = AdverseMediaAgent()

    assert agent._mock_sentiment("fraud case opened") == Sentiment.NEGATIVE
    assert agent._mock_sentiment("recognized for excellence") == Sentiment.POSITIVE
    assert agent._mock_sentiment("business news general") == Sentiment.NEUTRAL


def test_source_credibility():
    """Test source credibility scoring."""
    agent = AdverseMediaAgent()

    assert agent._source_credibility("Reuters", SourceType.NEWS) == 0.9
    assert agent._source_credibility("social", SourceType.SOCIAL) == 0.4
    assert agent._source_credibility("blog", SourceType.BLOG) == 0.6


def test_risk_level_values():
    """Test risk level enum values."""
    assert MediaRisk.LOW.value == "low"
    assert MediaRisk.MEDIUM.value == "medium"
    assert MediaRisk.HIGH.value == "high"
    assert MediaRisk.CRITICAL.value == "critical"


def test_sentiment_values():
    """Test sentiment enum values."""
    assert Sentiment.POSITIVE.value == "positive"
    assert Sentiment.NEGATIVE.value == "negative"
    assert Sentiment.NEUTRAL.value == "neutral"
    assert Sentiment.MIXED.value == "mixed"


def test_source_type_values():
    """Test source type enum values."""
    assert SourceType.NEWS.value == "news"
    assert SourceType.SOCIAL.value == "social"
    assert SourceType.REGULATORY.value == "regulatory"


def test_validate_context():
    """Test context validation."""
    agent = AdverseMediaAgent()

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
    agent = AdverseMediaAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={"full_name": "John Smith"},
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert "evidence" in result.data
    assert "articles_analyzed" in result.data["evidence"]


@pytest.mark.asyncio
async def test_article_serialization():
    """Test article serialization."""
    agent = AdverseMediaAgent()

    article = MediaArticle(
        id="1",
        title="Test Article",
        url="https://example.com",
        source="News",
        source_type=SourceType.NEWS,
        published_at=datetime.utcnow(),
        content="Test content",
        sentiment=Sentiment.NEUTRAL,
        confidence=0.8,
        relevance_score=0.9
    )

    result = agent._article_to_dict(article)

    assert result["id"] == "1"
    assert result["title"] == "Test Article"
    assert result["sentiment"] == "neutral"


@pytest.mark.asyncio
async def test_duplicate_elimination():
    """Test duplicate article elimination."""
    agent = AdverseMediaAgent()

    input_data = type('obj', (object,), {
        'full_name': 'John Smith',
        'country': 'US',
        'articles': [
            MediaArticle(
                id="1", title="Same Title", url="https://a.com",
                source="A", source_type=SourceType.NEWS,
                published_at=datetime.utcnow(), content="content",
                sentiment=Sentiment.NEUTRAL, confidence=0.8,
                relevance_score=0.9
            ),
            MediaArticle(
                id="2", title="Same Title", url="https://b.com",
                source="B", source_type=SourceType.NEWS,
                published_at=datetime.utcnow(), content="content",
                sentiment=Sentiment.NEUTRAL, confidence=0.8,
                relevance_score=0.9
            )
        ]
    })()

    result = agent._eliminate_duplicates(input_data)

    assert len(result.articles) == 1


@pytest.mark.asyncio
async def test_requires_review_flag():
    """Test review flag based on risk."""
    agent = AdverseMediaAgent()

    context = AgentContext(
        case_id="test-case-001",
        customer_id="test-customer-001",
        correlation_id="test-correlation-001",
        metadata={"full_name": "John Smith"},
        timestamp=datetime.utcnow()
    )

    result = await agent.execute(context)

    assert isinstance(result.requires_review, bool)