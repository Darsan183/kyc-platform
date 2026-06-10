# README - KYC Platform Production-Ready

## Autonomous Compliance Intelligence Platform (ACIP)

Enterprise-grade Agentic AI Powered KYC Intelligence Platform.

## Architecture Overview

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    └────────┬────────┘
                             │
            ┌────────────────┴────────────────┐
            │            Backend              │
            │    (Spring Boot - Java 21)       │
            └────────────────┬────────────────┘
                             │
            ┌────────────────┴────────────────┐
            │           Agents                │
            │     (FastAPI - Python 3.12)     │
            │ ┌───────────────────────────┐   │
            │ │ Document | Identity | AML  │   │
            │ │ Risk | Media | Audit     │   │
            │ └───────────────────────────┘   │
            └────────────────┬────────────────┘
                             │
        ┌─────────┬──────────┴──────────┬──────────┐
        │         │                     │          │
   ┌────┴──┐ ┌──┴──────┐         ┌────┴──┐  ┌───┴──────┐
   │ Redis │ │ Neo4j   │         │ Postgres │  │   S3    │
   │Cache  │ │Graph    │         │Primary  │  │(Documents│
   └───────┘ └─────────┘         └────────┘  └───┬───────┘
```

## Services

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| Backend API | 8080 | Spring Boot | REST API, authentication, business logic |
| Frontend | 3000 | Next.js 14 | React SPA with Material UI |
| Agents | 8000 | FastAPI | AI agents for KYC processing |
| PostgreSQL | 5432 | Postgres 16 | Primary relational database |
| Redis | 6379 | Redis 7 | Caching and message queue |
| Neo4j | 7687 | Neo4j 5 | Knowledge graph for relationship analysis |
| Prometheus | 9090 | Prometheus | Metrics collection |
| Grafana | 3001 | Grafana | Dashboard and visualization |
| OpenTelemetry | 4317 | OTEL Collector | Distributed tracing |

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with secure values

# 2. Build and start
docker-compose up -d

# 3. Verify services
docker-compose ps
curl http://localhost:8080/actuator/health
curl http://localhost:8000/health/
```

## Development

### Backend
```bash
cd kyc && ./mvnw spring-boot:run
```

### Frontend
```bash
cd kyc-frontend && npm run dev
```

### Agents
```bash
cd kyc/agents && uvicorn agents.main:app --reload
```

## API Endpoints

### Backend (Spring Boot)
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/customers` - List customers
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/cases/{id}` - Get case details
- `POST /api/v1/documents` - Upload document

### Agents (FastAPI)
- `GET /health/` - Health check
- `GET /api/agents` - List available agents
- `POST /api/workflows` - Execute workflow
- `POST /api/aml/screen` - AML screening
- `POST /api/risk/score` - Risk assessment

## Compliance Features

- SOC 2 Type II audit trails
- GDPR data retention policies
- PCI DSS data protection
- KYC/AML regulatory workflows
- Immutable audit logging

## Security Features

- JWT authentication (RS256 support)
- Role-based access control (RBAC)
- Rate limiting
- Input validation
- Security headers
- CORS protection

## Monitoring

- Prometheus metrics at `:9464/metrics`
- Health check endpoints
- Structured logging
- Audit trail export