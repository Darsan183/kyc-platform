"""Continuous Monitoring Models."""

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime
from enum import Enum


class MonitorType(str, Enum):
    """Types of monitoring."""
    NEWS_WATCH = "news_watch"
    SANCTIONS_WATCH = "sanctions_watch"
    REGULATORY_WATCH = "regulatory_watch"
    RISK_REVIEW = "risk_review"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status values."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


@dataclass
class MonitoringEvent:
    """Monitoring event detected."""
    event_id: str
    customer_id: str
    monitor_type: MonitorType
    detected_at: datetime
    source: str
    content: str
    risk_impact: float
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringAlert:
    """Alert generated from monitoring event."""
    alert_id: str
    customer_id: str
    severity: AlertSeverity
    status: AlertStatus
    monitor_type: MonitorType
    detected_at: datetime
    summary: str
    details: dict[str, Any]
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


@dataclass
class MonitoringSchedule:
    """Monitoring schedule configuration."""
    schedule_id: str
    customer_id: str
    monitor_types: list[MonitorType]
    frequency_hours: int
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True


@dataclass
class MonitoringResult:
    """Result of monitoring run."""
    run_id: str
    customer_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    events_detected: list[MonitoringEvent]
    alerts_generated: list[MonitoringAlert]
    risk_changes: dict[str, Any]
    status: str


@dataclass
class EscalationRule:
    """Rule for escalating alerts."""
    rule_id: str
    name: str
    condition: str
    severity_threshold: AlertSeverity
    escalation_target: str
    notification_channels: list[str]
    auto_escalate: bool = True


@dataclass
class NotificationChannel(str, Enum):
    """Notification channels."""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    SYSTEM = "system"


@dataclass
class Notification:
    """Notification to send."""
    notification_id: str
    alert_id: str
    channel: NotificationChannel
    recipient: str
    subject: str
    content: str
    sent_at: Optional[datetime] = None
    status: str = "pending"