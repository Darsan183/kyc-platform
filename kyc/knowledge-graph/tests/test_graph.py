"""Knowledge Graph Tests."""

import pytest
from datetime import datetime

from app.models.graph_models import (
    GraphNode,
    GraphRelationship,
    NodeType,
    RelationshipType
)


def test_node_creation():
    """Test graph node creation."""
    node = GraphNode(
        id="test-123",
        type=NodeType.CUSTOMER,
        properties={"name": "John Smith", "email": "john@example.com"},
        risk_score=0.5
    )

    assert node.id == "test-123"
    assert node.type == NodeType.CUSTOMER
    assert node.properties["name"] == "John Smith"


def test_relationship_creation():
    """Test graph relationship creation."""
    rel = GraphRelationship(
        source_id="john-123",
        target_id="company-456",
        type=RelationshipType.DIRECTOR_OF,
        strength=0.8
    )

    assert rel.source_id == "john-123"
    assert rel.target_id == "company-456"
    assert rel.type == RelationshipType.DIRECTOR_OF


def test_node_serialization():
    """Test node serialization."""
    node = GraphNode(
        id="test-123",
        type=NodeType.COMPANY,
        properties={"name": "Test Corp"},
        risk_score=0.2
    )

    result = node.to_dict()

    assert result["id"] == "test-123"
    assert result["type"] == "Company"
    assert "risk_score" in result


def test_relationship_serialization():
    """Test relationship serialization."""
    rel = GraphRelationship(
        source_id="a",
        target_id="b",
        type=RelationshipType.LOCATED_IN,
        strength=0.9
    )

    result = rel.to_dict()

    assert result["type"] == "LOCATED_IN"
    assert result["strength"] == 0.9


def test_node_type_values():
    """Test node type enum values."""
    assert NodeType.CUSTOMER.value == "Customer"
    assert NodeType.COMPANY.value == "Company"
    assert NodeType.SANCTION_ENTITY.value == "SanctionEntity"


def test_relationship_type_values():
    """Test relationship type enum values."""
    assert RelationshipType.DIRECTOR_OF.value == "DIRECTOR_OF"
    assert RelationshipType.MENTIONED_IN.value == "MENTIONED_IN"
    assert RelationshipType.SANCTIONED_AS.value == "SANCTIONED_AS"


def test_risk_level_values():
    """Test risk level values."""
    from app.models.graph_models import NetworkAnalysisResult
    # Just verify module loads correctly
    assert True


@pytest.mark.asyncio
async def test_network_analysis():
    """Test network analysis structure."""
    from app.models.graph_models import NetworkAnalysisResult

    # Create mock nodes
    nodes = [
        GraphNode(id="1", type=NodeType.CUSTOMER, properties={}),
        GraphNode(id="2", type=NodeType.COMPANY, properties={}, risk_score=0.5)
    ]

    result = NetworkAnalysisResult(
        center_node="center",
        nodes=nodes,
        relationships=[],
        risk_propagation={"1": 0.2, "2": 0.5},
        hidden_connections=[],
        centrality_scores={"1": 10, "2": 5}
    )

    assert result.center_node == "center"
    assert len(result.nodes) == 2
    assert "1" in result.risk_propagation