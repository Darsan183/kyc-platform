"""Identity Verification Agent - Enhanced Implementation."""

import logging
from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.agents.base import BaseAgent, AgentType, AgentContext, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class IdentityMatchLevel(str, Enum):
    """Identity match confidence levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NO_MATCH = "no_match"


class DuplicateRisk(str, Enum):
    """Duplicate detection risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class IdentityVerificationInput:
    """Input for identity verification."""
    full_name: str
    date_of_birth: str
    document_numbers: list[str]
    email: str
    phone: str
    address: str
    city: str
    state: str
    country: str
    documents: list[dict[str, Any]]


@dataclass
class IdentityVerificationOutput:
    """Output from identity verification."""
    match_level: IdentityMatchLevel
    confidence_score: float
    duplicate_risk: DuplicateRisk
    synthetic_risk: float
    cross_doc_issues: list[str]
    flags: list[str]
    recommendations: list[str]


class IdentityVerificationAgent(BaseAgent):
    """Enhanced identity verification agent with multiple verification layers."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(AgentType.IDENTITY, config)
        self._workflow = self._build_workflow()

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute identity verification workflow."""
        self.set_status(AgentStatus.RUNNING)

        try:
            # Parse input
            verification_input = self._parse_input(context)

            # Execute workflow
            output = self._workflow.invoke(verification_input)

            # Build result
            result = AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                score=output["confidence_score"],
                data={
                    "match_level": output["match_level"],
                    "duplicate_risk": output["duplicate_risk"],
                    "synthetic_risk": output["synthetic_risk"],
                    "cross_doc_issues": output["cross_doc_issues"],
                    "flags": output["flags"],
                    "recommendations": output["recommendations"],
                    "verified": output["confidence_score"] >= 0.7
                },
                requires_review=output["confidence_score"] < 0.8
            )

            self.set_status(AgentStatus.COMPLETED)
            return result

        except Exception as e:
            logger.error(f"Identity verification failed", exc_info=True)
            self.set_status(AgentStatus.FAILED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                errors=[str(e)]
            )

    def validate(self, context: AgentContext) -> bool:
        """Validate input has required fields."""
        required = ["full_name", "date_of_birth"]
        return any(field in context.metadata for field in required)

    def get_required_tools(self) -> list[str]:
        return [
            "identity_matcher",
            "duplicate_detector",
            "synthetic_identity_detector",
            "cross_document_validator"
        ]

    def _parse_input(self, context: AgentContext) -> dict[str, Any]:
        """Parse context into verification input."""
        return {
            "full_name": context.metadata.get("full_name", ""),
            "date_of_birth": context.metadata.get("date_of_birth", ""),
            "document_numbers": context.metadata.get("document_numbers", []),
            "email": context.metadata.get("email", ""),
            "phone": context.metadata.get("phone", ""),
            "address": context.metadata.get("address", ""),
            "city": context.metadata.get("city", ""),
            "state": context.metadata.get("state", ""),
            "country": context.metadata.get("country", ""),
            "documents": context.metadata.get("documents", [])
        }

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for identity verification."""
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("identity_matching", self._identity_matching)
        workflow.add_node("duplicate_detection", self._duplicate_detection)
        workflow.add_node("synthetic_detection", self._synthetic_detection)
        workflow.add_node("cross_doc_validation", self._cross_document_validation)
        workflow.add_node("confidence_scoring", self._calculate_confidence)
        workflow.add_node("decision_making", self._make_decision)

        # Define flow
        workflow.set_entry_point("identity_matching")
        workflow.add_edge("identity_matching", "duplicate_detection")
        workflow.add_edge("duplicate_detection", "synthetic_detection")
        workflow.add_edge("synthetic_detection", "cross_doc_validation")
        workflow.add_edge("cross_doc_validation", "confidence_scoring")
        workflow.add_edge("confidence_scoring", "decision_making")
        workflow.add_edge("decision_making", END)

        return workflow.compile()

    def _identity_matching(self, state: dict[str, Any]) -> dict[str, Any]:
        """Perform identity matching across documents."""
        full_name = state.get("full_name", "")
        documents = state.get("documents", [])

        matches = []
        name_variants = self._generate_name_variants(full_name)

        for doc in documents:
            doc_name = doc.get("extracted_name", "")
            match_score = self._calculate_name_match(doc_name, name_variants)
            matches.append({
                "document": doc.get("type"),
                "match_score": match_score,
                "name_found": doc_name
            })

        avg_match = sum(m["match_score"] for m in matches) / len(matches) if matches else 0

        state["identity_matches"] = matches
        state["match_level"] = self._get_match_level(avg_match).value

        return state

    def _duplicate_detection(self, state: dict[str, Any]) -> dict[str, Any]:
        """Check for duplicate identities in database."""
        # Mock duplicate check - in production would query database
        name_hash = hash(state.get("full_name", ""))
        doc_nums = state.get("document_numbers", [])

        # Simulate duplicate risk based on patterns
        risk_score = min(len(doc_nums) * 0.1 + (name_hash % 50) / 100, 1.0)
        state["duplicate_risk"] = (
            DuplicateRisk.HIGH.value if risk_score > 0.7
            else DuplicateRisk.MEDIUM.value if risk_score > 0.4
            else DuplicateRisk.LOW.value
        )
        state["duplicate_score"] = risk_score

        return state

    def _synthetic_detection(self, state: dict[str, Any]) -> dict[str, Any]:
        """Detect synthetic identity patterns."""
        # Check for synthetic identity indicators
        full_name = state.get("full_name", "").lower()
        dob = state.get("date_of_birth", "")

        flags = []
        risk_score = 0.0

        # Check for generic names
        generic_names = ["john doe", "jane smith", "customer", "user"]
        if any(name in full_name for name in generic_names):
            flags.append("generic_name_pattern")
            risk_score += 0.3

        # Check for sequential document numbers
        doc_nums = state.get("document_numbers", [])
        if len(doc_nums) >= 2:
            if self._is_sequential(doc_nums):
                flags.append("sequential_document_numbers")
                risk_score += 0.4

        # Check for invalid DOB patterns
        if dob and self._is_suspicious_dob(dob):
            flags.append("suspicious_date_of_birth")
            risk_score += 0.3

        state["synthetic_risk"] = min(risk_score, 1.0)
        state["synthetic_flags"] = flags

        return state

    def _cross_document_validation(self, state: dict[str, Any]) -> dict[str, Any]:
        """Cross-validate information across documents."""
        documents = state.get("documents", [])
        issues = []

        if len(documents) < 2:
            return {**state, "cross_doc_issues": issues}

        # Extract fields from all documents
        extracted_dobs = [doc.get("date_of_birth") for doc in documents]
        addresses = [doc.get("address") for doc in documents]

        # Check DOB consistency
        unique_dobs = set(extracted_dobs)
        if len(unique_dobs) > 1:
            issues.append(f"Inconsistent DOB across documents: {list(unique_dobs)}")

        state["cross_doc_issues"] = issues
        return state

    def _calculate_confidence(self, state: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall confidence score."""
        # Weight factors
        match_weight = 0.4
        duplicate_weight = -0.2  # Negative weight
        synthetic_weight = -0.3  # Negative weight
        cross_doc_weight = 0.1

        # Get scores
        match_score = self._match_level_to_score(state.get("match_level", "no_match"))
        duplicate_score = state.get("duplicate_score", 0.0)
        synthetic_score = state.get("synthetic_risk", 0.0)
        cross_doc_penalty = len(state.get("cross_doc_issues", [])) * 0.15

        confidence = (
            match_score * match_weight +
            (1 - duplicate_score) * duplicate_weight +
            (1 - synthetic_score) * synthetic_weight +
            (1 - cross_doc_penalty) * cross_doc_weight
        )

        state["confidence_score"] = max(0.0, min(1.0, confidence))
        return state

    def _make_decision(self, state: dict[str, Any]) -> dict[str, Any]:
        """Make final verification decision."""
        confidence = state.get("confidence_score", 0.0)
        flags = state.get("synthetic_flags", [])

        all_flags = flags + state.get("cross_doc_issues", [])

        if confidence >= 0.8 and len(all_flags) == 0:
            state["decision"] = "VERIFIED"
            state["recommendations"] = ["Proceed to AML screening"]
        elif confidence >= 0.6:
            state["decision"] = "REVIEW_REQUIRED"
            state["recommendations"] = ["Manual review recommended", "Additional verification needed"]
        else:
            state["decision"] = "REJECTED"
            state["recommendations"] = ["Identity verification failed", "Reject application"]

        state["flags"] = all_flags
        return state

    # Helper methods
    def _generate_name_variants(self, full_name: str) -> list[str]:
        """Generate name variants for matching."""
        variants = [full_name.lower()]
        parts = full_name.split()
        if len(parts) > 1:
            variants.append(f"{parts[-1].lower()}, {parts[0][0].upper()}.")
            variants.append(parts[0].lower())
        return variants

    def _calculate_name_match(self, extracted: str, variants: list[str]) -> float:
        """Calculate name match score."""
        if not extracted:
            return 0.0

        extracted_lower = extracted.lower()
        for variant in variants:
            if variant in extracted_lower or extracted_lower in variant:
                return 0.95

        # Check partial matches
        extracted_parts = extracted_lower.split()
        variant_parts = variants[0].split()

        matches = sum(1 for ep in extracted_parts if any(vp in ep for vp in variant_parts))
        return matches / max(len(extracted_parts), len(variant_parts))

    def _get_match_level(self, score: float) -> IdentityMatchLevel:
        """Convert score to match level."""
        if score >= 0.9:
            return IdentityMatchLevel.HIGH
        elif score >= 0.7:
            return IdentityMatchLevel.MEDIUM
        elif score >= 0.4:
            return IdentityMatchLevel.LOW
        else:
            return IdentityMatchLevel.NO_MATCH

    def _match_level_to_score(self, level: str) -> float:
        """Convert match level to numeric score."""
        return {
            "high": 1.0,
            "medium": 0.7,
            "low": 0.4,
            "no_match": 0.0
        }.get(level, 0.0)

    def _is_sequential(self, numbers: list[str]) -> bool:
        """Check if document numbers are suspiciously sequential."""
        if len(numbers) < 2:
            return False
        # Simple heuristic - in production would be more sophisticated
        return numbers[0][-2:] == numbers[1][-2:]

    def _is_suspicious_dob(self, dob: str) -> bool:
        """Check for suspicious date of birth patterns."""
        suspicious_dates = ["1900-01-01", "2000-01-01", "1970-01-01"]
        return dob in suspicious_dates


# Prompt templates
IDENTITY_MATCHING_PROMPT = """
You are an expert identity verification specialist. Analyze the following identity information
from multiple documents and determine if they belong to the same person.

Customer Name: {full_name}
Date of Birth: {date_of_birth}
Documents Found: {documents}

Provide:
1. Match confidence (HIGH/MEDIUM/LOW/NO_MATCH)
2. Key matching indicators
3. Any discrepancies found
"""

SYNTHETIC_IDENTITY_PROMPT = """
Analyze the following identity data for synthetic identity fraud patterns:

Name: {full_name}
DOB: {date_of_birth}
Document Numbers: {document_numbers}
Email: {email}
Phone: {phone}

Look for:
1. Generic or obviously fake names
2. Sequential or patterned document numbers
3. Suspicious date of birth (e.g., round numbers)
4. Inconsistent formatting across fields
"""

CROSS_DOCUMENT_PROMPT = """
Cross-validate identity information across the following documents:

Documents: {documents}

Check for:
1. Consistency in name spelling
2. Matching date of birth
3. Address consistency
4. Document number patterns
"""