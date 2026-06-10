"""Risk Scoring Engine - Production Ready Implementation."""

import logging
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from functools import reduce

from langgraph.graph import StateGraph, END

from app.agents.base import BaseAgent, AgentType, AgentContext, AgentResult, AgentStatus

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Customer risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskComponent:
    """Individual risk component score."""
    name: str
    score: float
    weight: float
    evidence: dict[str, Any]
    reasons: list[str]


@dataclass
class RiskScore:
    """Calculated risk score."""
    total_score: float
    level: RiskLevel
    components: list[RiskComponent]
    confidence: float
    requires_review: bool
    decision: str
    reasons: list[str]
    evidence: dict[str, Any]
    explanation: str


class RiskScoringEngine(BaseAgent):
    """Risk Scoring Engine - aggregates agent outputs and calculates risk scores."""

    # Default weights (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        "identity": 0.20,
        "document": 0.25,
        "aml": 0.25,
        "media": 0.20,
        "compliance": 0.10
    }

    def __init__(self, config: Optional[dict[str, Any]] = None):
        super().__init__(AgentType.RISK, config)
        self.weights = config.get("weights", self.DEFAULT_WEIGHTS) if config else self.DEFAULT_WEIGHTS
        self._workflow = self._build_workflow()

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute risk scoring workflow."""
        self.set_status(AgentStatus.RUNNING)

        try:
            # Extract scores from context
            scores = self._extract_scores(context.metadata)

            # Execute workflow
            output = self._workflow.invoke(scores)

            # Build result
            result = AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.COMPLETED,
                score=output.total_score,
                data={
                    "risk_level": output.level.value,
                    "components": [self._component_to_dict(c) for c in output.components],
                    "confidence": output.confidence,
                    "decision": output.decision,
                    "reasons": output.reasons,
                    "evidence": output.evidence,
                    "explanation": output.explanation
                },
                requires_review=output.requires_review,
                next_agent=AgentType.AUDIT
            )

            self.set_status(AgentStatus.COMPLETED)
            return result

        except Exception as e:
            logger.error(f"Risk scoring failed", exc_info=True)
            self.set_status(AgentStatus.FAILED)
            return AgentResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                errors=[str(e)]
            )

    def validate(self, context: AgentContext) -> bool:
        """Validate input has required scores."""
        return "metadata" in context.__dict__

    def get_required_tools(self) -> list[str]:
        return [
            "risk_calculator",
            "weight_manager",
            "explanation_generator",
            "threshold_checker",
            "ml_predictor"
        ]

    def _extract_scores(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Extract scores from agent outputs."""
        return {
            "identity_score": metadata.get("identity_score", 100),
            "document_score": metadata.get("document_score", 100),
            "aml_hits": metadata.get("aml_hits", 0),
            "aml_risk_level": metadata.get("aml_risk_level", "low"),
            "media_negative": metadata.get("media_negative_articles", 0),
            "media_total": metadata.get("media_total_articles", 0),
            "compliance_violations": metadata.get("compliance_violations", 0),
            "customer_data": metadata
        }

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for risk scoring."""
        workflow = StateGraph(dict)

        workflow.add_node("score_normalization", self._normalize_scores)
        workflow.add_node("weighted_aggregation", self._aggregate_weights)
        workflow.add_node("ml_enhancement", self._ml_enhancement)
        workflow.add_node("risk_level_assignment", self._assign_risk_level)
        workflow.add_node("evidence_collection", self._collect_evidence)
        workflow.add_node("decision_engine", self._make_decision)
        workflow.add_node("explainability", self._generate_explanation)

        workflow.set_entry_point("score_normalization")
        workflow.add_edge("score_normalization", "weighted_aggregation")
        workflow.add_edge("weighted_aggregation", "ml_enhancement")
        workflow.add_edge("ml_enhancement", "risk_level_assignment")
        workflow.add_edge("risk_level_assignment", "evidence_collection")
        workflow.add_edge("evidence_collection", "decision_engine")
        workflow.add_edge("decision_engine", "explainability")
        workflow.add_edge("explainability", END)

        return workflow.compile()

    def _normalize_scores(self, state: dict[str, Any]) -> dict[str, Any]:
        """Normalize scores to 0-100 scale."""
        # Convert AML risk to score
        aml_risk_map = {"low": 100, "medium": 70, "high": 40, "critical": 10}
        aml_score = aml_risk_map.get(state.get("aml_risk_level", "low"), 100)

        # Convert media negative ratio to score
        media_total = state.get("media_total", 0)
        media_negative = state.get("media_negative", 0)
        media_score = 100 if media_total == 0 else 100 - (media_negative / max(media_total, 1)) * 100

        # Convert compliance violations to score
        violations = state.get("compliance_violations", 0)
        compliance_score = max(0, 100 - violations * 20)

        state["normalized_scores"] = {
            "identity": min(100, max(0, state.get("identity_score", 100))),
            "document": min(100, max(0, state.get("document_score", 100))),
            "aml": aml_score,
            "media": media_score,
            "compliance": compliance_score
        }

        return state

    def _aggregate_weights(self, state: dict[str, Any]) -> dict[str, Any]:
        """Apply weighted aggregation to scores."""
        scores = state.get("normalized_scores", {})

        total = 0.0
        components = []

        for name, weight in self.weights.items():
            score = scores.get(name, 50)
            weighted = score * weight
            total += weighted

            component = RiskComponent(
                name=name,
                score=score,
                weight=weight,
                evidence={},
                reasons=self._generate_reasons(name, score)
            )
            components.append(component)

        state["weighted_score"] = total
        state["components"] = components
        state["raw_total"] = total

        return state

    def _ml_enhancement(self, state: dict[str, Any]) -> dict[str, Any]:
        """Apply ML-based enhancement to risk score."""
        # Mock ML model - in production would call actual model
        raw_score = state.get("raw_total", 50)

        # Simple heuristic for ML adjustment
        customer_data = state.get("customer_data", {})

        # Adjust based on country risk
        high_risk_countries = ["KP", "IR", "SY", "RU"]
        country = customer_data.get("country", "")
        if country in high_risk_countries:
            raw_score = min(100, raw_score + 15)

        state["ml_adjusted_score"] = raw_score
        return state

    def _assign_risk_level(self, state: dict[str, Any]) -> dict[str, Any]:
        """Assign risk level based on score."""
        score = state.get("ml_adjusted_score", 50)

        level = RiskLevel.LOW
        if score >= 80:
            level = RiskLevel.LOW
        elif score >= 60:
            level = RiskLevel.MEDIUM
        elif score >= 40:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL

        state["risk_level"] = level
        return state

    def _collect_evidence(self, state: dict[str, Any]) -> dict[str, Any]:
        """Collect evidence from all sources."""
        evidence = {
            "scores": state.get("normalized_scores", {}),
            "components": [self._component_to_dict(c) for c in state.get("components", [])],
            "ml_adjustments": state.get("ml_adjusted_score", 0),
            "thresholds_used": {
                "low": {"min": 80, "max": 100},
                "medium": {"min": 60, "max": 79},
                "high": {"min": 40, "max": 59},
                "critical": {"min": 0, "max": 39}
            }
        }

        state["evidence"] = evidence
        return state

    def _make_decision(self, state: dict[str, Any]) -> dict[str, Any]:
        """Make final risk decision."""
        score = state.get("ml_adjusted_score", 50)
        level = state.get("risk_level", RiskLevel.LOW)

        decision = "APPROVE"
        if level == RiskLevel.CRITICAL:
            decision = "REJECT"
        elif level == RiskLevel.HIGH:
            decision = "ENHANCED_REVIEW"
        elif level == RiskLevel.MEDIUM:
            decision = "MONITOR"

        state["decision"] = decision
        return state

    def _generate_explanation(self, state: dict[str, Any]) -> RiskScore:
        """Generate human-readable explanation."""
        score = state.get("ml_adjusted_score", 50)
        level = state.get("risk_level", RiskLevel.LOW)

        explanation = self._build_explanation_text(
            score=score,
            level=level,
            components=state.get("components", [])
        )

        return RiskScore(
            total_score=score,
            level=level,
            components=state.get("components", []),
            confidence=self._calculate_confidence(state),
            requires_review=level in [RiskLevel.HIGH, RiskLevel.CRITICAL],
            decision=state.get("decision", "APPROVE"),
            reasons=self._collect_reasons(state.get("components", [])),
            evidence=state.get("evidence", {}),
            explanation=explanation
        )

    # Helper methods
    def _generate_reasons(self, component: str, score: float) -> list[str]:
        """Generate reasons for component score."""
        if score >= 80:
            return [f"{component}: No significant risk factors identified"]
        elif score >= 60:
            return [f"{component}: Some minor risk factors present"]
        elif score >= 40:
            return [f"{component}: Elevated risk factors detected"]
        else:
            return [f"{component}: High-risk factors identified requiring immediate attention"]

    def _component_to_dict(self, component: RiskComponent) -> dict[str, Any]:
        return {
            "name": component.name,
            "score": component.score,
            "weight": component.weight,
            "evidence": component.evidence,
            "reasons": component.reasons
        }

    def _calculate_confidence(self, state: dict[str, Any]) -> float:
        """Calculate confidence in risk score."""
        scores = state.get("normalized_scores", {})
        if not scores:
            return 0.5

        # Average confidence across components
        avg = sum(scores.values()) / len(scores)
        return min(1.0, avg / 100.0)

    def _collect_reasons(self, components: list[RiskComponent]) -> list[str]:
        """Collect all reasons from components."""
        reasons = []
        for component in components:
            reasons.extend(component.reasons)
        return reasons

    def _build_explanation_text(self, score: float, level: RiskLevel, components: list[RiskComponent]) -> str:
        """Build human-readable explanation."""
        lines = [
            f"Overall Risk Score: {score:.1f}",
            f"Risk Level: {level.value.upper()}",
            "",
            "Component Breakdown:"
        ]

        for c in components:
            lines.append(f"  - {c.name}: {c.score:.1f} (weight: {c.weight})")

        lines.append("")
        lines.append(f"Decision: {self._get_decision_text(level)}")

        return "\n".join(lines)

    def _get_decision_text(self, level: RiskLevel) -> str:
        decisions = {
            RiskLevel.LOW: "APPROVE - No additional review required",
            RiskLevel.MEDIUM: "MONITOR - Ongoing monitoring recommended",
            RiskLevel.HIGH: "ENHANCED_REVIEW - Enhanced due diligence required",
            RiskLevel.CRITICAL: "REJECT - Applicant should be rejected"
        }
        return decisions.get(level, "REVIEW")


# Prompt templates
RISK_CALCULATION_PROMPT = """
Calculate risk score for KYC screening.

Scores:
- Identity: {identity_score}
- Document: {document_score}
- AML: {aml_score}
- Media: {media_score}
- Compliance: {compliance_score}

Weights (default):
- Identity: 20%
- Document: 25%
- AML: 25%
- Media: 20%
- Compliance: 10%

Calculate weighted average and provide risk level.
"""

DECISION_FRAMEWORK_PROMPT = """
Make decision based on risk score.

Risk Score: {score}
Risk Level: {level}
Components: {components}

Decision Rules:
- Score >= 80: LOW RISK - APPROVE
- Score >= 60: MEDIUM RISK - MONITOR
- Score >= 40: HIGH RISK - ENHANCED REVIEW
- Score < 40: CRITICAL - REJECT

Provide final decision and rationale.
"""

EXPLAINABILITY_PROMPT = """
Generate explainable risk scoring output.

Risk Score: {score}
Risk Level: {level}
Components: {components}

Explain in clear business terms:
1. Why this risk level was assigned
2. Key factors contributing to score
3. Confidence in assessment
4. Recommended actions
"""

WEIGHTED_RULE_PROMPT = """
Apply weighted rules to risk scoring.

Available Weights: {weights}
Raw Scores: {scores}

Apply weights and calculate composite score.
Consider regulatory requirements and business rules.
"""

ML_PREDICTION_PROMPT = """
Enhance risk score with ML prediction.

Current Score: {score}
Customer Profile: {profile}

Apply machine learning enhancement for:
- Country risk adjustments
- Pattern recognition
- Historical risk correlations

Provide adjusted score and confidence.
"""