"""Audit Reporting Service."""

import hashlib
import json
from datetime import datetime
from typing import Any, Optional, List
import io

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from jinja2 import Template
import structlog

from app.models.audit_models import (
    AuditReport,
    RegulatorReport,
    AuditPackage,
    ReportType,
    AgentExecutionLog,
    Evidence,
    DecisionTrace
)

logger = structlog.get_logger()


class PDFGenerator:
    """PDF generation service using ReportLab."""

    @staticmethod
    def generate_case_report(report: AuditReport) -> bytes:
        """Generate PDF for case report."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(f"KYC CASE REPORT: {report.case_id}", styles["Title"]))
        elements.append(Spacer(1, 20))

        # Summary
        elements.append(Paragraph("Executive Summary", styles["Heading1"]))
        elements.append(Paragraph(report.summary, styles["Normal"]))
        elements.append(Spacer(1, 20))

        # Events table
        elements.append(Paragraph("Audit Trail", styles["Heading1"]))
        event_data = [["Timestamp", "Event Type", "Actor"]]
        for event in report.events[:10]:
            event_data.append([
                event.timestamp.strftime("%Y-%m-%d %H:%M"),
                event.event_type.value,
                event.actor
            ])

        event_table = Table(event_data)
        event_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(event_table)

        doc.build(elements)
        return buffer.getvalue()

    @staticmethod
    def generate_risk_report(case_id: str, risk_score: float, factors: dict[str, Any]) -> bytes:
        """Generate PDF for risk report."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"RISK REPORT: {case_id}", styles["Title"]))
        elements.append(Spacer(1, 20))

        elements.append(Paragraph(f"Risk Score: {risk_score}", styles["Heading1"]))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph("Risk Factors:", styles["Heading2"]))
        for factor, value in factors.items():
            elements.append(Paragraph(f"- {factor}: {value}", styles["Normal"]))

        doc.build(elements)
        return buffer.getvalue()


class AuditService:
    """Audit reporting service."""

    def __init__(self, db_connection_string: Optional[str] = None):
        self.reports: dict[str, AuditReport] = {}
        self.pdf_generator = PDFGenerator()

    def collect_audit_events(self, case_id: str) -> List[Any]:
        """Collect audit events for a case."""
        # Mock implementation - in production would query database
        return []

    def collect_evidence(self, case_id: str) -> List[Evidence]:
        """Collect evidence for a case."""
        return []

    def collect_agent_logs(self, case_id: str) -> List[AgentExecutionLog]:
        """Collect agent execution logs."""
        return []

    def collect_decision_traces(self, case_id: str) -> List[DecisionTrace]:
        """Collect decision traces."""
        return []

    def generate_case_report(self, case_id: str, generated_by: str) -> AuditReport:
        """Generate comprehensive case report."""
        events = self.collect_audit_events(case_id)
        evidence = self.collect_evidence(case_id)
        agent_logs = self.collect_agent_logs(case_id)
        decision_traces = self.collect_decision_traces(case_id)

        report = AuditReport(
            report_id=f"RPT-{case_id}-{int(datetime.utcnow().timestamp())}",
            case_id=case_id,
            report_type=ReportType.CASE_REPORT,
            generated_at=datetime.utcnow(),
            generated_by=generated_by,
            events=events,
            evidence=evidence,
            agent_logs=agent_logs,
            decision_traces=decision_traces,
            summary=f"Case {case_id} processed with {len(events)} audit events"
        )

        self.reports[report.report_id] = report
        return report

    def generate_regulator_report(self, case_id: str, regulator: str) -> RegulatorReport:
        """Generate regulator-ready report."""
        case_report = self.generate_case_report(case_id, "system")

        return RegulatorReport(
            report_id=f"REG-{case_id}",
            case_id=case_id,
            report_type=ReportType.REGULATOR_REPORT,
            generated_at=datetime.utcnow(),
            generated_by="system",
            events=case_report.events,
            evidence=case_report.evidence,
            agent_logs=case_report.agent_logs,
            decision_traces=case_report.decision_traces,
            summary=case_report.summary,
            regulator=regulator,
            filing_date=datetime.utcnow(),
            sar_filed=False,
            regulatory_reference=""
        )

    def generate_audit_package(self, case_id: str) -> AuditPackage:
        """Generate complete audit package."""
        case_report = self.generate_case_report(case_id, "system")
        evidence = self.collect_evidence(case_id)

        package_id = f"PKG-{case_id}-{int(datetime.utcnow().timestamp())}"

        # Calculate checksum
        checksum = hashlib.sha256(
            json.dumps([e.to_dict() for e in evidence]).encode()
        ).hexdigest()

        return AuditPackage(
            package_id=package_id,
            case_id=case_id,
            created_at=datetime.utcnow(),
            reports=[case_report],
            evidence=evidence,
            metadata={"case_count": 1},
            checksum=checksum
        )

    def to_pdf(self, report: AuditReport) -> bytes:
        """Convert report to PDF."""
        if report.report_type == ReportType.CASE_REPORT:
            return self.pdf_generator.generate_case_report(report)
        elif report.report_type == ReportType.RISK_REPORT:
            return self.pdf_generator.generate_risk_report(
                report.case_id, 0.0, {}
            )
        return b""

    def export_json(self, report: AuditReport) -> str:
        """Export report as JSON."""
        return json.dumps({
            "report_id": report.report_id,
            "case_id": report.case_id,
            "report_type": report.report_type.value,
            "generated_at": report.generated_at.isoformat(),
            "summary": report.summary,
            "events_count": len(report.events),
            "evidence_count": len(report.evidence)
        }, indent=2)


# Jinja2 templates
CASE_REPORT_TEMPLATE = """
# KYC Case Report: {{ case_id }}

## Executive Summary
{{ summary }}

## Audit Trail
{% for event in events %}
- {{ event.timestamp }}: {{ event.event_type }} by {{ event.actor }}
{% endfor %}

## Evidence Collected
{% for evidence in evidence %}
- {{ evidence.type }}: {{ evidence.source }}
{% endfor %}

## Agent Executions
{% for log in agent_logs %}
- {{ log.agent_type }}: {{ log.status }}
{% endfor %}
"""

REGULATOR_REPORT_TEMPLATE = """
KYC REGULATOR REPORT - {{ regulator }}

Case Reference: {{ case_id }}
Report Date: {{ generated_at }}
Filing: {{ 'SAR Filed' if sar_filed else 'No SAR' }}

## Summary
{{ summary }}

## Findings
{% for trace in decision_traces %}
Decision: {{ trace.decision }}
Reason: {{ trace.reason }}
{% endfor %}
"""


def render_template(template: str, context: dict[str, Any]) -> str:
    """Render Jinja2 template."""
    return Template(template).render(**context)