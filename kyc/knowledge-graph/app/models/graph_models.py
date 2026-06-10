"""Knowledge Graph Models - Neo4j Node and Relationship Definitions."""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
from datetime import datetime


class NodeType(str, Enum):
    """Node types in the knowledge graph."""
    CUSTOMER = "Customer"
    COMPANY = "Company"
    DIRECTOR = "Director"
    BENEFICIAL_OWNER = "BeneficialOwner"
    COUNTRY = "Country"
    SANCTION_ENTITY = "SanctionEntity"
    MEDIA_EVENT = "MediaEvent"


class RelationshipType(str, Enum):
    """Relationship types in the knowledge graph."""
    # Ownership relationships
    DIRECTOR_OF = "DIRECTOR_OF"
    BENEFICIAL_OWNER_OF = "BENEFICIAL_OWNER_OF"
    SUBSCRIBER_OF = "SUBSCRIBER_OF"
    
    # Geographic relationships
    LOCATED_IN = "LOCATED_IN"
    REGISTERED_IN = "REGISTERED_IN"
    
    # Risk relationships
    SANCTIONED_AS = "SANCTIONED_AS"
    MENTIONED_IN = "MENTIONED_IN"
    RELATED_TO = "RELATED_TO"
    
    # Identity relationships
    SAME_AS = "SAME_AS"
    ALIAS_OF = "ALIAS_OF"
    
    # Business relationships
    ACQUAINTANCE_OF = "ACQUAINTANCE_OF"
    BUSINESS_PARTNER_OF = "BUSINESS_PARTNER_OF"


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""
    id: str
    type: NodeType
    properties: dict[str, Any] = field(default_factory=dict)
    risk_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "properties": self.properties,
            "risk_score": self.risk_score,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class GraphRelationship:
    """Represents a relationship in the knowledge graph."""
    source_id: str
    target_id: str
    type: RelationshipType
    properties: dict[str, Any] = field(default_factory=dict)
    strength: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            "properties": self.properties,
            "strength": self.strength
        }


@dataclass
class CustomerNode(GraphNode):
    """Customer node with KYC-specific properties."""
    def __init__(self, customer_id: str, **kwargs):
        super().__init__(
            id=customer_id,
            type=NodeType.CUSTOMER,
            properties=kwargs
        )


@dataclass
class CompanyNode(GraphNode):
    """Company node for business relationships."""
    def __init__(self, company_id: str, **kwargs):
        super().__init__(
            id=company_id,
            type=NodeType.COMPANY,
            properties=kwargs
        )


@dataclass
class SanctionEntityNode(GraphNode):
    """Sanctioned entity node."""
    def __init__(self, entity_id: str, **kwargs):
        super().__init__(
            id=entity_id,
            type=NodeType.SANCTION_ENTITY,
            properties=kwargs
        )


@dataclass
class MediaEventNode(GraphNode):
    """Media event node for adverse media."""
    def __init__(self, event_id: str, **kwargs):
        super().__init__(
            id=event_id,
            type=NodeType.MEDIA_EVENT,
            properties=kwargs
        )


@dataclass
class NetworkAnalysisResult:
    """Result of network analysis."""
    center_node: str
    nodes: list[GraphNode]
    relationships: list[GraphRelationship]
    risk_propagation: dict[str, float]
    hidden_connections: list[dict[str, Any]]
    centrality_scores: dict[str, float]
    cluster_info: dict[str, Any]