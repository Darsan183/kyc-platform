# KYC Agents - AI Agent Framework

Autonomous Compliance Intelligence Platform - AI Agents Module

## Overview

This module implements AI agents for automated KYC processing using LangGraph and FastAPI.

## Agents

- **Document Agent** - Document validation and OCR
- **Identity Agent** - Identity verification
- **AML Agent** - Sanctions and watchlist screening
- **Adverse Media Agent** - Negative media analysis
- **Compliance Agent** - Regulatory compliance checking
- **Risk Agent** - Risk scoring and assessment
- **Audit Agent** - Audit trail generation

## Quick Start

```bash
# Install dependencies
poetry install

# Run the server
poetry run uvicorn app.main:app --reload --port 8000

# Run tests
poetry run pytest
```