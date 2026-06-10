"""Continuous Monitoring Agent - Main Agent Implementation."""

import logging
from datetime import datetime
from typing import Any, Optional

from langgraph.graph import StateGraph, END

from app.models.monitoring_models import (
    MonitoringEvent,
    MonitoringAlert,
    MonitoringResult,
    MonitorType,
    AlertSeverity,
    AlertStatus
)

logger = logging.getLogger(__name__)


class MonitoringAgent:
    """Continuous monitoring agent that tracks customers after onboarding."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self._workflow = self._build_workflow()

    async def monitor_customer(self, customer_id: str, customer_data: dict[str, Any]) -> MonitoringResult:
        """Run monitoring for a customer."""
        run_id = f"MON-{customer_id}-{int(datetime.utcnow().timestamp())}"

        state = {
            "customer_id": customer_id,
            "customer_data": customer_data,
            "run_id": run_id,
            "started_at": datetime.utcnow(),
            "events": [],
            "alerts": [],
            "risk_changes": {}
        }

        result = self._workflow.invoke(state)

        return MonitoringResult(
            run_id=run_id,
            customer_id=customer_id,
            started_at=state["started_at"],
            completed_at=datetime.utcnow(),
            events_detected=result["events"],
            alerts_generated=result["alerts"],
            risk_changes=result["risk_changes"],
            status="completed"
        )

    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for monitoring."""
        workflow = StateGraph(dict)

        workflow.add_node("news_monitor", self._check_news)
        workflow.add_node("sanctions_monitor", self._check_sanctions)
        workflow.add_node("regulatory_monitor", self._check_regulatory)
        workflow.add_node("risk_assessment", self._assess_risk_changes)
        workflow.add_node("alert_generation", self._generate_alerts)

        workflow.set_entry_point("news_monitor")
        workflow.add_edge("news_monitor", "sanctions_monitor")
        workflow.add_edge("sanctions_monitor", "regulatory_monitor")
        workflow.add_edge("regulatory_monitor", "risk_assessment")
        workflow.add_edge("risk_assessment", "alert_generation")
        workflow.add_edge("alert_generation", END)

        return workflow.compile()

    def _check_news(self, state: dict[str, Any]) -> dict[str, Any]:
        """Check for news about customer."""
        events = []
        customer_id = state["customer_id"]
        customer_data = state["customer_data"]
        full_name = customer_data.get("full_name", "")

        # Mock news check - in production would call news API
        if "test" not in full_name.lower():
            events.append(MonitoringEvent(
                event_id=f"EVT-{customer_id}-001",
                customer_id=customer_id,
                monitor_type=MonitorType.NEWS_WATCH,
                detected_at=datetime.utcnow(),
                source="news_api",
                content="No adverse news found in recent search",
                risk_impact=0.0,
                details={"search_completed": True}
            ))

        state["events"] = events
        return state

    def _check_sanctions(self, state: dict[str, Any]) -> dict[str, Any]:
        """Check sanctions lists for updates."""
        events = state.get("events", [])
        customer_id = state["customer_id"]

        # Mock sanctions check
        events.append(MonitoringEvent(
            event_id=f"EVT-{customer_id}-002",
            customer_id=customer_id,
            monitor_type=MonitorType.SANCTIONS_WATCH,
            detected_at=datetime.utcnow(),
            source="sanctions_db",
            content="Sanctions check completed - no updates",
            risk_impact=0.0,
            details={"hits": 0}
        ))

        state["events"] = events
        return state

    def _check_regulatory(self, state: dict[str, Any]) -> dict[str, Any]:
        """Check regulatory updates."""
        events = state.get("events", [])
        customer_id = state["customer_id"]

        events.append(MonitoringEvent(
            event_id=f"EVT-{customer_id}-003",
            customer_id=customer_id,
            monitor_type=MonitorType.REGULATORY_WATCH,
            detected_at=datetime.utcnow(),
            source="regulatory_feed",
            content="No regulatory updates affecting customer",
            risk_impact=0.0,
            details={"regulations_checked": 5}
        ))

        state["events"] = events
        return state

    def _assess_risk_changes(self, state: dict[str, Any]) -> dict[str, Any]:
        """Assess risk score changes."""
        events = state.get("events", [])

        # Calculate risk impact
        total_impact = sum(e.risk_impact for e in events)

        state["risk_changes"] = {
            "delta": total_impact,
            "previous_score": state["customer_data"].get("risk_score", 50),
            "new_score": max(0, min(100, 50 + total_impact * 10))
        }

        return state

    def _generate_alerts(self, state: dict[str, Any]) -> dict[str, Any]:
        """Generate alerts based on events."""
        events = state.get("events", [])
        alerts = []

        high_impact_events = [e for e in events if e.risk_impact > 0.5]

        for event in high_impact_events:
            alert = MonitoringAlert(
                alert_id=f"ALERT-{event.event_id}",
                customer_id=event.customer_id,
                severity=self._severity_from_impact(event.risk_impact),
                status=AlertStatus.OPEN,
                monitor_type=event.monitor_type,
                detected_at=event.detected_at,
                summary=f"Risk event detected: {event.content}",
                details=event.details
            )
            alerts.append(alert)

        state["alerts"] = alerts
        return state

    def _severity_from_impact(self, impact: float) -> AlertSeverity:
        """Convert impact to severity."""
        if impact >= 0.8:
            return AlertSeverity.CRITICAL
        elif impact >= 0.5:
            return AlertSeverity.HIGH
        elif impact >= 0.2:
            return AlertSeverity.MEDIUM
        return AlertSeverity.LOW


# Prompt templates
MONITORING_SUMMARY_PROMPT = """
Generate a monitoring summary for the following customer.

Customer: {customer_id}
Events Detected: {events}
Risk Changes: {risk_changes}

Provide:
1. Summary of findings
2. Risk assessment changes
3. Recommended actions
"""

ALERT_GENERATION_PROMPT = """
Generate alert details for the following monitoring event.

Event: {event}
Customer: {customer_id}
Risk Impact: {impact}

Create alert with:
1. Severity level
2. Action items
3. Escalation recommendation
"""

ESCALATION_DECISION_PROMPT = """
Determine escalation path for alert.

Alert: {alert}
Severity: {severity}
Assigned To: {assigned_to}

Decide:
1. Should escalate?
2. Target for escalation
3. Notification channels
"""