# Production Deployment Guide

## Prerequisites
- Docker >= 24.0
- Docker Compose >= 2.20
- Java 21 (for local build)
- Node.js 20+ (for local build)

## Environment Setup

1. Copy `.env.example` to `.env` and configure values:
```bash
cp .env.example .env
# Edit .env with your production values
```

2. Generate a secure JWT secret (32+ characters):
```bash
openssl rand -base64 32
```

## Local Development

```bash
# Build all services
docker-compose -f docker-compose.yml build

# Start all services
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose -f docker-compose.yml logs -f

# Stop services
docker-compose -f docker-compose.yml down
```

## Production Deployment

### Docker Compose (Recommended for single-node)
```bash
# With production environment
docker-compose -f docker-compose.yml --env-file .env up -d
```

### Kubernetes (Helm-based)
```bash
# Install dependencies
helm dependency update kyc/infrastructure/helm

# Deploy to production
helm upgrade --install kyc-platform kyc/infrastructure/helm \
  --namespace kyc-platform --create-namespace \
  --set image.repository=ghcr.io/your-org/kyc-platform \
  --set image.tag=latest \
  --set postgresql.auth.password=$(kubectl get secret kyc-postgres -o jsonpath='{.data.postgres-password}' | base64 -d)
```

## Security Checklist
- [ ] JWT_SECRET configured with 32+ characters
- [ ] Database credentials changed from defaults
- [ ] Redis password configured
- [ ] HTTPS/TLS enabled at load balancer
- [ ] CORS origins restricted to production domains
- [ ] Database backups configured
- [ ] Log aggregation configured

## Health Endpoints
- Backend: http://localhost:8080/actuator/health
- Agents: http://localhost:8000/health/
- Prometheus: http://localhost:9090