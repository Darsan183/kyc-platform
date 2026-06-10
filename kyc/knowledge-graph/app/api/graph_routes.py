"""Knowledge Graph API Endpoints."""

from typing import Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import structlog

from app.services.graph_service import KnowledgeGraphService, NetworkResponse
from app.models.graph_models import GraphNode, GraphRelationship, NodeType, RelationshipType

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])
logger = structlog.get_logger()


class CreateNodeRequest(BaseModel):
    """Request to create a node."""
    node_id: str
    node_type: str
    properties: dict[str, Any] = Field(default_factory=dict)
    risk_score: Optional[float] = 0.0


class CreateRelationshipRequest(BaseModel):
    """Request to create a relationship."""
    source_id: str
    target_id: str
    relationship_type: str
    properties: dict[str, Any] = Field(default_factory=dict)
    strength: float = 1.0


def get_graph_service() -> KnowledgeGraphService:
    """Get graph service instance."""
    return KnowledgeGraphService(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password"
    )


@router.post("/nodes")
async def create_node(request: CreateNodeRequest):
    """Create a node in the knowledge graph."""
    service = get_graph_service()

    node = GraphNode(
        id=request.node_id,
        type=NodeType(request.node_type),
        properties=request.properties,
        risk_score=request.risk_score
    )

    result = service.create_node(node)
    return {"node": result}


@router.post("/relationships")
async def create_relationship(request: CreateRelationshipRequest):
    """Create a relationship in the knowledge graph."""
    service = get_graph_service()

    rel = GraphRelationship(
        source_id=request.source_id,
        target_id=request.target_id,
        type=RelationshipType(request.relationship_type),
        properties=request.properties,
        strength=request.strength
    )

    result = service.create_relationship(rel)
    return {"relationship": result}


@router.get("/network/{customer_id}")
async def get_network(customer_id: str, depth: int = 3):
    """Get customer network connections."""
    service = get_graph_service()

    nodes = service.find_connected_customers(customer_id, max_depth=depth)

    return NetworkResponse(
        center_node=customer_id,
        nodes=[n.to_dict() for n in nodes],
        relationships=[],
        risk_propagation={},
        hidden_connections=[],
        centrality_scores={}
    )


@router.post("/risk/propagate")
async def propagate_risk(customer_id: str, risk_score: float, depth: int = 3):
    """Propagate risk through network."""
    service = get_graph_service()

    result = service.propagate_risk(customer_id, risk_score)
    return {"propagated": result}


@router.get("/analysis/{customer_id}")
async def analyze_network(customer_id: str):
    """Perform comprehensive network analysis."""
    service = get_graph_service()

    analysis = service.analyze_network(customer_id)

    return {
        "center_node": analysis.center_node,
        "nodes": [n.to_dict() for n in analysis.nodes],
        "risk_propagation": analysis.risk_propagation,
        "hidden_connections": analysis.hidden_connections,
        "centrality_scores": analysis.centrality_scores
    }


@router.get("/hidden-connections/{customer_id}")
async def find_hidden_connections(customer_id: str):
    """Find hidden connections using alias detection."""
    service = get_graph_service()

    result = service.find_hidden_connections(customer_id)
    return result


@router.get("/circular-ownership")
async def detect_circular_ownership():
    """Detect circular ownership patterns."""
    service = get_graph_service()

    result = service.detect_circular_ownership()
    return {"circular_ownership": result}


@router.get("/sanction-paths/{customer_id}")
async def find_sanction_paths(customer_id: str):
    """Find sanction entity paths from customer."""
    return {
        "paths": [],
        "customer_id": customer_id
    }