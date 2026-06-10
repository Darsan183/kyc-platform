"""Monitoring Module Tests."""

import pytest
from datetime import datetime

from app.models.monitoring_models import (
    MonitoringEvent,
    MonitoringAlert,
    MonitoringSchedule,
    AlertSeverity,
    AlertStatus,
    MonitorType
)
from app.agents.monitoring_agent import MonitoringAgent


@pytest.mark.asyncio
async def test_monitoring_agent():
    """Test monitoring agent execution."""
    agent = MonitoringAgent()

    result = await agent.monitor_customer("test-customer-001", {"full_name": "Test User"})

    assert result.customer_id == "test-customer-001"
    assert result.status == "completed"


def test_monitoring_event():
    """Test monitoring event creation."""
    event = MonitoringEvent(
        event_id="EVT-001",
        customer_id="CUST-001",
        monitor_type=MonitorType.NEWS_WATCH,
        detected_at=datetime.utcnow(),
        source="news_api",
        content="Test event",
        risk_impact=0.3
    )

    assert event.monitor_type == MonitorType.NEWS_WATCH
    assert event.risk_impact == 0.3


def test_monitoring_alert():
    """Test monitoring alert creation."""
    alert = MonitoringAlert(
        alert_id="ALERT-001",
        customer_id="CUST-001",
        severity=AlertSeverity.HIGH,
        status=AlertStatus.OPEN,
        monitor_type=MonitorType.SANCTIONS_WATCH,
        detected_at=datetime.utcnow(),
        summary="Test alert summary",
        details={"impact": 0.8}
    )

    assert alert.severity == AlertSeverity.HIGH
    assert alert.status == AlertStatus.OPEN


def test_monitoring_schedule():
    """Test monitoring schedule creation."""
    schedule = MonitoringSchedule(
        schedule_id="SCHED-001",
        customer_id="CUST-001",
        monitor_types=[MonitorType.NEWS_WATCH],
        frequency_hours=24,
        enabled=True
    )

    assert schedule.customer_id == "CUST-001"
    assert schedule.frequency_hours == 24


def test_severity_from_impact():
    """Test severity calculation from impact."""
    agent = MonitoringAgent()

    assert agent._severity_from_impact(0.9) == AlertSeverity.CRITICAL
    assert agent._severity_from_impact(0.6) == AlertSeverity.HIGH
    assert agent._severity_from_impact(0.3) == AlertSeverity.MEDIUM
    assert agent._severity_from_impact(0.1) == AlertSeverity.LOW


@pytest.mark.asyncio
async def test_manual_check():
    """Test manual monitoring check."""
    from app.services.monitoring_service import MonitoringService

    service = MonitoringService()

    result = await service.run_manual_check(
        "test-customer-001",
        {"full_name": "Test User", "risk_score": 50}
    )

    assert result.customer_id == "test-customer-001"
    assert "run_id" in result.__dict__


def test_monitor_type_values():
    """Test monitor type enum values."""
    assert MonitorType.NEWS_WATCH.value == "news_watch"
    assert MonitorType.SANCTIONS_WATCH.value == "sanctions_watch"


def test_alert_severity_values():
    """Test alert severity enum values."""
    assert AlertSeverity.LOW.value == "low"
    assert AlertSeverity.CRITICAL.value == "critical"