"""Observability Service - logging, metrics, and tracing."""

import structlog
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from typing import Optional


def setup_logging() -> None:
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def setup_observability(
    otlp_endpoint: Optional[str] = None,
    service_name: str = "kyc-agents"
) -> None:
    """Setup OpenTelemetry tracing and metrics."""
    
    resource = Resource(attributes={
        "service.name": service_name,
        "service.version": "1.0.0"
    })

    # Tracing
    tracer_provider = TracerProvider(resource=resource)
    if otlp_endpoint:
        span_processor = BatchSpanProcessor(
            OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        )
        tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    # Metrics
    meter_provider = MeterProvider(resource=resource)
    if otlp_endpoint:
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
        )
        meter_provider._metric_readers.append(reader)
    metrics.set_meter_provider(meter_provider)


class AgentMetrics:
    """Metrics for agent execution."""

    def __init__(self):
        meter = metrics.get_meter("kyc-agents")
        self.execution_counter = meter.create_counter(
            name="agent_executions_total",
            description="Total agent executions"
        )
        self.duration_histogram = meter.create_histogram(
            name="agent_execution_duration_seconds",
            description="Agent execution duration"
        )
        self.error_counter = meter.create_counter(
            name="agent_errors_total",
            description="Total agent errors"
        )

    def record_execution(self, agent_type: str, status: str, duration: float) -> None:
        self.execution_counter.add(1, {"agent_type": agent_type, "status": status})
        self.duration_histogram.record(duration, {"agent_type": agent_type})

    def record_error(self, agent_type: str, error: str) -> None:
        self.error_counter.add(1, {"agent_type": agent_type, "error": error})


# Global instances
logger = structlog.get_logger()
agent_metrics = AgentMetrics()