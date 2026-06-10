# Agent Development Guide

## Architecture

This platform uses an agent-based architecture for KYC processing. Each agent handles a specific compliance domain.

## Agents

| Agent | Responsibility | Input | Output |
|-------|-------------|-------|--------|
| DocumentAgent | Document OCR, validation, forgery detection | Document files, metadata | Extracted data, authenticity score |
| IdentityAgent | Identity verification, biometric matching | Customer identity data | Verification status, confidence score |
| AmlAgent | Sanctions, watchlist, PEP screening | Customer name, DOB, address | AML hits, risk level |
| MediaAgent | Adverse media analysis | Customer name | Media articles, sentiment score |
| RiskAgent | Composite risk scoring | All agent outputs | Risk score, level, decision |
| AuditAgent | Audit trail generation | Workflow results | Audit records, compliance evidence |
| MonitoringAgent | Continuous monitoring | Customer profiles | Alerts, monitoring results |

## Running Agents

```bash
# Start all services
docker-compose up -d

# Check agent health
curl http://localhost:8000/health/

# Execute a workflow
curl -X POST http://localhost:8000/api/workflows \
  -H "Content-Type: application/json" \
  -d '{"case_id": "uuid", "customer_data": {...}}'
```

## Agent Configuration

Agents can be configured via environment variables:

```yaml
environment:
  - RISK_WEIGHTS_IDENTITY=0.20
  - RISK_WEIGHTS_DOCUMENT=0.25
  - RISK_WEIGHTS_AML=0.25
  - RISK_WEIGHTS_MEDIA=0.20
  - RISK_WEIGHTS_COMPLIANCE=0.10
```

## Inter-Agent Communication

Agents communicate via the `AgentOrchestrator` which:
1. Processes cases sequentially through the workflow
2. Passes context between agents
3. Handles failures and retries
4. Generates final audit trail