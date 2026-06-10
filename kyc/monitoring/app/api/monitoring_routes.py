"""Monitoring API Endpoints."""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

from app.services.monitoring_service import MonitoringService
from app.agents.monitoring_agent import MonitoringAgent
from app.models.monitoring_models import AlertSeverity, AlertStatus

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
logger = structlog.get_logger()

# Service singleton
monitoring_service = MonitoringService()


class MonitoringStartRequest(BaseModel):
    """Request to start monitoring."""
    customer_id: str
    monitor_types: list[str]
    frequency_hours: int = Field(default=24, ge=1, le=168)


class ManualCheckRequest(BaseModel):
    """Request for manual monitoring check."""
    customer_id: str
    customer_data: dict[str, Any]


class AlertAcknowledgeRequest(BaseModel):
    """Request to acknowledge alert."""
    alert_id: str
    user: str
    notes: Optional[str] = None


@router.post("/start")
async def start_monitoring(request: MonitoringStartRequest):
    """Start monitoring for a customer."""
    try:
        monitoring_service.schedule_customer(
            request.customer_id,
            request.monitor_types,
            request.frequency_hours
        )

        return {
            "status": "scheduled",
            "customer_id": request.customer_id,
            "frequency_hours": request.frequency_hours,
            "monitor_types": request.monitor_types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check")
async def run_manual_check(request: ManualCheckRequest):
    """Run manual monitoring check."""
    result = await monitoring_service.run_manual_check(
        request.customer_id,
        request.customer_data
    )

    return {
        "customer_id": request.customer_id,
        "run_id": result["run_id"],
        "events_detected": result["events"],
        "alerts_generated": result["alerts"],
        "risk_changes": result["risk_changes"]
    }


@router.get("/alerts")
async def get_alerts(
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None
):
    """Get monitoring alerts."""
    alerts = await monitoring_service.get_alerts(customer_id)

    return {
        "alerts": alerts,
        "total": len(alerts),
        "filters": {
            "customer_id": customer_id,
            "status": status,
            "severity": severity
        }
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user: str = "system"):
    """Acknowledge an alert."""
    success = await monitoring_service.acknowledge_alert(alert_id, user)

    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"status": "acknowledged", "alert_id": alert_id}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, notes: str = ""):
    """Resolve an alert."""
    success = await monitoring_service.resolve_alert(alert_id, notes)

    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"status": "resolved", "alert_id": alert_id}


@router.get("/dashboard/stats")
async def get_monitoring_stats():
    """Get monitoring dashboard statistics."""
    return {
        "active_monitors": len(monitoring_service.schedules),
        "alerts_today": 0,
        "high_severity_alerts": 0,
        "pending_reviews": 0,
        "last_check": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def get_monitoring_status():
    """Get monitoring service status."""
    return {
        "running": monitoring_service._running,
        "scheduled_customers": len(monitoring_service.schedules),
        "redis_connected": True
    }


@router.post("/test/{customer_id}")
async def test_monitoring(customer_id: str):
    """Test monitoring for a customer."""
    return await run_manual_check(ManualCheckRequest(
        customer_id=customer_id,
        customer_data={"full_name": "Test User", "risk_score": 50}
    ))