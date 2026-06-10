"""Monitoring Service - Core Service Implementation."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, List
from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import redis.asyncio as redis
import structlog

from app.agents.monitoring_agent import MonitoringAgent
from app.models.monitoring_models import (
    MonitoringSchedule,
    MonitoringAlert,
    AlertStatus,
    AlertSeverity,
    Notification,
    NotificationChannel
)

logger = structlog.get_logger()


class MonitoringService:
    """Core monitoring service with scheduling and notification capabilities."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.agent = MonitoringAgent()
        self.scheduler = AsyncIOScheduler()
        self.redis_client = redis.from_url(redis_url)
        self.schedules: dict[str, MonitoringSchedule] = {}
        self._running = False

    async def start(self):
        """Start the monitoring service."""
        self.scheduler.start()
        self._running = True
        logger.info("Monitoring service started")

    async def stop(self):
        """Stop the monitoring service."""
        self.scheduler.shutdown()
        self._running = False
        logger.info("Monitoring service stopped")

    def schedule_customer(self, customer_id: str, monitor_types: List[str], frequency_hours: int = 24):
        """Schedule monitoring for a customer."""
        schedule = MonitoringSchedule(
            schedule_id=str(uuid4()),
            customer_id=customer_id,
            monitor_types=monitor_types,
            frequency_hours=frequency_hours,
            next_run=datetime.utcnow() + timedelta(hours=frequency_hours),
            enabled=True
        )

        self.schedules[schedule.schedule_id] = schedule

        self.scheduler.add_job(
            self._run_monitoring_job,
            trigger=IntervalTrigger(hours=frequency_hours),
            args=[customer_id],
            id=schedule.schedule_id,
            replace_existing=True
        )

        logger.info(f"Scheduled monitoring for customer {customer_id}")

    async def run_manual_check(self, customer_id: str, customer_data: dict[str, Any]) -> dict[str, Any]:
        """Run manual monitoring check."""
        result = await self.agent.monitor_customer(customer_id, customer_data)

        # Store result
        await self.redis_client.setex(
            f"monitoring:{result.run_id}",
            86400,
            str(result)
        )

        # Generate alerts if needed
        for alert in result.alerts_generated:
            await self._process_alert(alert)

        return {
            "run_id": result.run_id,
            "events": len(result.events_detected),
            "alerts": len(result.alerts_generated),
            "risk_changes": result.risk_changes
        }

    async def get_alerts(self, customer_id: Optional[str] = None, status: Optional[str] = None) -> List[dict[str, Any]]:
        """Get alerts for customer or all."""
        # Mock implementation
        return []

    async def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert."""
        return True

    async def resolve_alert(self, alert_id: str, notes: str) -> bool:
        """Resolve an alert."""
        return True

    async def _run_monitoring_job(self, customer_id: str):
        """Scheduled monitoring job."""
        logger.info(f"Running scheduled monitoring for {customer_id}")

        customer_data = await self.redis_client.hgetall(f"customer:{customer_id}")
        if not customer_data:
            return

        await self.run_manual_check(customer_id, customer_data)

    async def _process_alert(self, alert: MonitoringAlert):
        """Process generated alert."""
        # Send notifications
        await self._send_notifications(alert)

        # Check escalation rules
        await self._check_escalation(alert)

    async def _send_notifications(self, alert: MonitoringAlert):
        """Send notifications for alert."""
        channels = [NotificationChannel.SYSTEM]

        for channel in channels:
            notification = Notification(
                notification_id=str(uuid4()),
                alert_id=alert.alert_id,
                channel=channel,
                recipient=alert.assigned_to or "compliance-team",
                subject=f"[{alert.severity.value.upper()}] Alert for {alert.customer_id}",
                content=alert.summary
            )

            # Store notification
            await self.redis_client.lpush(
                f"notifications:{alert.customer_id}",
                str(notification)
            )

    async def _check_escalation(self, alert: MonitoringAlert):
        """Check escalation rules."""
        if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            # Escalate to supervisor
            alert.status = AlertStatus.ESCALATED
            alert.assigned_to = "supervisor"


class NotificationService:
    """Notification delivery service."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)

    async def send_notification(self, notification: Notification) -> bool:
        """Send a notification."""
        try:
            if notification.channel == NotificationChannel.EMAIL:
                return await self._send_email(notification)
            elif notification.channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(notification)
            return await self._send_system(notification)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    async def _send_email(self, notification: Notification) -> bool:
        """Send email notification."""
        # Mock email sending
        logger.info(f"Email sent to {notification.recipient}")
        return True

    async def _send_webhook(self, notification: Notification) -> bool:
        """Send webhook notification."""
        # Mock webhook sending
        logger.info(f"Webhook sent to {notification.recipient}")
        return True

    async def _send_system(self, notification: Notification) -> bool:
        """Send system notification."""
        # Store in Redis for UI pickup
        await self.redis_client.publish(
            f"notifications:{notification.recipient}",
            str(notification)
        )
        return True

    async def get_user_notifications(self, user_id: str, limit: int = 50) -> List[Notification]:
        """Get notifications for user."""
        # Mock implementation
        return []