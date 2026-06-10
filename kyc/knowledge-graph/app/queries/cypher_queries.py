"""Cypher Queries for Knowledge Graph Operations."""

from typing import Any


class CypherQueries:
    """Collection of Cypher queries for graph operations."""

    # Node creation queries
    CREATE_CUSTOMER = """
    MERGE (c:Customer {customerId: $customer_id})
    SET c.name = $name,
        c.email = $email,
        c.riskScore = $risk_score,
        c.createdAt = $created_at
    RETURN c
    """

    CREATE_COMPANY = """
    MERGE (co:Company {companyId: $company_id})
    SET co.name = $name,
        co.registrationNumber = $reg_number,
        co.jurisdiction = $jurisdiction,
        co.riskScore = $risk_score
    RETURN co
    """

    CREATE_SANCTION_ENTITY = """
    MERGE (s:SanctionEntity {entityId: $entity_id})
    SET s.name = $name,
        s.listType = $list_type,
        s.country = $country,
        s.program = $program
    RETURN s
    """

    CREATE_MEDIA_EVENT = """
    MERGE (m:MediaEvent {eventId: $event_id})
    SET m.headline = $headline,
        m.source = $source,
        m.sentiment = $sentiment,
        m.publishedAt = $published_at
    RETURN m
    """

    # Relationship queries
    REL_DIRECTOR = """
    MATCH (d:Director {directorId: $director_id})
    MATCH (c:Company {companyId: $company_id})
    MERGE (d)-[r:DIRECTOR_OF {
        since: $since,
        position: $position
    }]->(c)
    SET r.strength = $strength
    RETURN r
    """

    REL_BENEFICIAL_OWNER = """
    MATCH (bo:BeneficialOwner {ownerId: $owner_id})
    MATCH (c:Company {companyId: $company_id})
    MERGE (bo)-[r:BENEFICIAL_OWNER_OF {
        since: $since,
        percentage: $percentage
    }]->(c)
    SET r.strength = $strength
    RETURN r
    """

    REL_SANCTIONED = """
    MATCH (c:Customer {customerId: $customer_id})
    MATCH (s:SanctionEntity {entityId: $entity_id})
    MERGE (c)-[r:SANCTIONED_AS]->(s)
    SET r.confidence = $confidence,
        r.matchedOn = $matched_on
    RETURN r
    """

    REL_MEDIA_MENTION = """
    MATCH (c:Customer {customerId: $customer_id})
    MATCH (m:MediaEvent {eventId: $event_id})
    MERGE (c)-[r:MENTIONED_IN {
        context: $context,
        sentimentMatch: $sentiment_match
    }]->(m)
    RETURN r
    """

    # Search queries
    FIND_CUSTOMER_NETWORK = """
    MATCH (c:Customer {customerId: $customer_id})
    MATCH path = (c)-[r*1..4]-(connected)
    RETURN DISTINCT connected, length(path) as distance
    LIMIT $limit
    """

    FIND_HIDDEN_CONNECTIONS = """
    MATCH (c1:Customer {customerId: $customer1_id})
    MATCH (c2:Customer {customerId: $customer2_id})
    MATCH path = allShortestPaths((c1)-[*..5]-(c2))
    WHERE NONE(rel IN relationships(path) WHERE type(rel) = 'SAME_AS')
    RETURN path
    """

    FIND_SANCTION_PATHS = """
    MATCH (c:Customer {customerId: $customer_id})
    MATCH (s:SanctionEntity)
    MATCH path = shortestPath((c)-[*..4]-(s))
    WHERE length(path) > 0
    RETURN s, length(path) as distance, nodes(path) as path_nodes
    """

    FIND_CIRCULAR_OWNERSHIP = """
    MATCH (c:Company)-[:BENEFICIAL_OWNER_OF*2..4]->(c)
    RETURN c, count(*) as cycle_length
    """

    # Risk propagation queries
    PROPAGATE_RISK = """
    MATCH (source:Customer {customerId: $source_id})
    MATCH (source)-[r:RELATED_TO*1..3]->(target)
    WITH target, reduce(risk = 0, rel IN relationships(path) | risk + coalesce(rel.strength, 0.5)) as propagated_risk
    SET target.riskScore = coalesce(target.riskScore, 0) + propagated_risk * 0.1
    RETURN target.customerId, target.riskScore
    """

    # Analysis queries
    CALCULATE_CENTRALITY = """
    MATCH (c:Customer {customerId: $customer_id})
    MATCH (connected) WHERE connected <> c
    OPTIONAL MATCH (c)-[r]-(connected)
    WITH connected, count(r) as connections
    RETURN connected.customerId as node, connections
    ORDER BY connections DESC
    LIMIT 20
    """

    FIND_COMMON_CONNECTIONS = """
    MATCH (c1:Customer {customerId: $customer1_id})
    MATCH (c2:Customer {customerId: $customer2_id})
    MATCH (c1)-[r1]-(common)
    MATCH (c2)-[r2]-(common)
    RETURN common, count(r1) + count(r2) as connection_strength
    ORDER BY connection_strength DESC
    """

    # Cleanup queries
    DELETE_CUSTOMER = """
    MATCH (c:Customer {customerId: $customer_id})
    DETACH DELETE c
    """

    DELETE_ORPHAN_NODES = """
    MATCH (n)
    WHERE NOT (n)--() AND n:Customer OR n:Company
    DELETE n
    """


class GraphQueries:
    """Graph query builder and executor."""

    def __init__(self, driver):
        self.driver = driver

    def create_customer(self, customer_id: str, name: str, email: str, risk_score: float = 0.0) -> Any:
        """Create customer node."""
        with self.driver.session() as session:
            result = session.run(
                CypherQueries.CREATE_CUSTOMER,
                customer_id=customer_id,
                name=name,
                email=email,
                risk_score=risk_score,
                created_at=str(datetime.utcnow())
            )
            return result.single()

    def find_network(self, customer_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Find customer network connections."""
        with self.driver.session() as session:
            result = session.run(
                CypherQueries.FIND_CUSTOMER_NETWORK,
                customer_id=customer_id,
                limit=limit
            )
            return [dict(record) for record in result]

    def find_sanction_paths(self, customer_id: str) -> list[dict[str, Any]]:
        """Find sanction entity paths."""
        with self.driver.session() as session:
            result = session.run(
                CypherQueries.FIND_SANCTION_PATHS,
                params={"customer_id": customer_id}
            )
            return [dict(record) for record in result]


import datetime