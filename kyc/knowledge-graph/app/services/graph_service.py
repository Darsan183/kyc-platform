"""Neo4j Knowledge Graph Service."""

from typing import Any, Optional, List
from datetime import datetime

from neo4j import GraphDatabase
from pydantic import BaseModel
import structlog

from app.models.graph_models import (
    GraphNode,
    GraphRelationship,
    NodeType,
    RelationshipType,
    NetworkAnalysisResult
)

logger = structlog.get_logger()


class KnowledgeGraphService:
    """Neo4j-based knowledge graph service."""

    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the driver connection."""
        self.driver.close()

    def create_node(self, node: GraphNode) -> dict[str, Any]:
        """Create a node in the graph."""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_node_tx,
                node_id=node.id,
                node_type=node.type.value,
                properties=node.properties,
                risk_score=node.risk_score or 0.0
            )
            return result

    def create_relationship(self, rel: GraphRelationship) -> dict[str, Any]:
        """Create a relationship in the graph."""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_relationship_tx,
                source_id=rel.source_id,
                target_id=rel.target_id,
                rel_type=rel.type.value,
                properties=rel.properties,
                strength=rel.strength
            )
            return result

    def find_connected_customers(self, customer_id: str, max_depth: int = 3) -> List[GraphNode]:
        """Find all customers connected to given customer."""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_connected_tx,
                customer_id=customer_id,
                max_depth=max_depth
            )
            return result

    def propagate_risk(self, customer_id: str, risk_score: float) -> List[dict[str, Any]]:
        """Propagate risk scores through the network."""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._propagate_risk_tx,
                customer_id=customer_id,
                risk_score=risk_score
            )
            return result

    def find_hidden_connections(self, customer_id: str) -> dict[str, Any]:
        """Find hidden connections using multiple paths."""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_hidden_tx,
                customer_id=customer_id
            )
            return result

    def calculate_centrality(self, customer_id: str) -> dict[str, float]:
        """Calculate centrality scores for network analysis."""
        with self.driver.session() as session:
            result = session.read_transaction(
                self._calculate_centrality_tx,
                customer_id=customer_id
            )
            return result

    def detect_circular_ownership(self) -> List[dict[str, Any]]:
        """Detect circular ownership patterns."""
        with self.driver.session() as session:
            result = session.read_transaction(self._detect_circular_tx)
            return result

    def analyze_network(self, customer_id: str) -> NetworkAnalysisResult:
        """Perform comprehensive network analysis."""
        connections = self.find_connected_customers(customer_id)
        centrality = self.calculate_centrality(customer_id)
        hidden = self.find_hidden_connections(customer_id)

        risk_propagation = {
            node.id: node.risk_score or 0.0
            for node in connections
        }

        return NetworkAnalysisResult(
            center_node=customer_id,
            nodes=connections,
            relationships=[],
            risk_propagation=risk_propagation,
            hidden_connections=hidden.get("connections", []),
            centrality_scores=centrality,
            cluster_info={}
        )

    # Transaction methods
    @staticmethod
    def _create_node_tx(tx, node_id: str, node_type: str, properties: dict, risk_score: float):
        query = f"""
        MERGE (n:{node_type} {{id: $node_id}})
        SET n += $properties
        SET n.riskScore = $risk_score
        RETURN n
        """
        result = tx.run(query, node_id=node_id, properties=properties, risk_score=risk_score)
        return result.single()

    @staticmethod
    def _create_relationship_tx(tx, source_id: str, target_id: str, rel_type: str, properties: dict, strength: float):
        query = f"""
        MATCH (s {{id: $source_id}})
        MATCH (t {{id: $target_id}})
        MERGE (s)-[r:{rel_type}]->(t)
        SET r += $properties
        SET r.strength = $strength
        RETURN r
        """
        result = tx.run(query, source_id=source_id, target_id=target_id, properties=properties, strength=strength)
        return result.single()

    @staticmethod
    def _find_connected_tx(tx, customer_id: str, max_depth: int):
        query = """
        MATCH (c:Customer {customerId: $customer_id})
        MATCH path = (c)-[r*1..$max_depth]-(connected)
        RETURN DISTINCT connected
        """
        result = tx.run(query, customer_id=customer_id, max_depth=max_depth)
        return [GraphNode(id=record["connected"].id, type=NodeType.CUSTOMER, properties=dict(record["connected"])) 
                for record in result]

    @staticmethod
    def _propagate_risk_tx(tx, customer_id: str, risk_score: float):
        query = """
        MATCH (source:Customer {customerId: $customer_id})
        MATCH (source)-[r:RELATED_TO*1..3]->(target)
        SET target.riskScore = coalesce(target.riskScore, 0) + $risk_score * 0.1
        RETURN target.customerId as customerId, target.riskScore as riskScore
        """
        result = tx.run(query, customer_id=customer_id, risk_score=risk_score)
        return [dict(record) for record in result]

    @staticmethod
    def _find_hidden_tx(tx, customer_id: str):
        query = """
        MATCH (c:Customer {customerId: $customer_id})
        MATCH (c)-[r:ALIAS_OF*1..2]-(alias)
        OPTIONAL MATCH (alias)-[r2]-(connected)
        WHERE NOT (c)-[r3]-(connected)
        RETURN collect(DISTINCT connected) as connections
        """
        result = tx.run(query, customer_id=customer_id)
        record = result.single()
        return {"connections": record["connections"] if record else []}

    @staticmethod
    def _calculate_centrality_tx(tx, customer_id: str):
        query = """
        MATCH (c:Customer {customerId: $customer_id})
        MATCH (connected) WHERE connected <> c
        OPTIONAL MATCH (c)-[r]-(connected)
        RETURN connected.customerId as node, count(r) as score
        """
        result = tx.run(query, customer_id=customer_id)
        return {record["node"]: record["score"] for record in result}

    @staticmethod
    def _detect_circular_tx(tx):
        query = """
        MATCH cycle = (c:Company)-[:BENEFICIAL_OWNER_OF*2..4]->(c)
        RETURN c.companyName as company, length(cycle) as cycle_length
        """
        result = tx.run(query)
        return [dict(record) for record in result]


# Response models
class NetworkResponse(BaseModel):
    """Network analysis response."""
    center_node: str
    nodes: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    risk_propagation: dict[str, float]
    hidden_connections: list[dict[str, Any]]
    centrality_scores: dict[str, float]


class RiskPropagationRequest(BaseModel):
    """Request for risk propagation."""
    customer_id: str
    risk_score: float
    propagate_depth: int = 3