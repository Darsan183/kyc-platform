"""Audit Reporting Models."""

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    """Types of audit reports."""
    CASE_REPORT = "case_report"
    RISK_REPORT = "risk_report"
    REGULATOR_REPORT = "regulator_report"
    AUDIT_PACKAGE = "audit_package"
    COMPLIANCE_REPORT = "compliance_report"


class AuditEventType(str, Enum):
    """Types of audit events."""
    CASE_CREATED = "case_created"
    DOCUMENT_UPLOADED = "document_uploadloaded"
    VERIFICATION_COMPLETED = "verification_completed"
    AGENT_EXECUTED = "agent_executed"
    DECISION_MADE = "decision_made"
    CASE_APPROVED = "case_approved"
    CASE_REJECTED = "case_rejected"


@dataclass
class AuditEvent:
    """Represents an audit event."""
    id: str
    case_id: str
    event_type: AuditEventType
    timestamp: datetime
    actor: str
    data: dict[str, Any]
    correlation_id: str


@dataclass
class Evidence:
    """Evidence collected during processing."""
    evidence_id: str
    case_id: str
    type: str
    source: str
    content: Any
    hash: str
    collected_at: datetime


@dataclass
class AgentExecutionLog:
    """Agent execution log entry."""
    execution_id: str
    agent_type: str
    case_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    errors: list[str]


@dataclass
class DecisionTrace:
    """Decision traceability record."""
    decision_id: str
    case_id: str
    decision: str
    reason: str
    made_by: str
    made_at: datetime
    agent_results: dict[str, Any]
    evidence_refs: list[str]
    regulatory_basis: list[str]


@dataclass
class AuditReport:
    """Audit report model."""
    report_id: str
    case_id: str
    report_type: ReportType
    generated_at: datetime
    generated_by: str
    events: list[AuditEvent]
    evidence: list[Evidence]
    agent_logs: list[AgentExecutionLog]
    decision_traces: list[DecisionTrace]
    summary: str


@dataclass
class RegulatorReport(AuditReport):
    """Regulator-ready report with specific formatting."""
    regulator: str
    filing_date: datetime
    sar_filed: bool
    regulatory_reference: str


@dataclass
class AuditPackage:
    """Complete audit package for submission."""
    package_id: str
    case_id: str
    created_at: datetime
    reports: list[AuditReport]
    evidence: list[Evidence]
    metadata: dict[str, Any]
    checksum: str