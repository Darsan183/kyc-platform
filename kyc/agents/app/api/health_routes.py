"""Health API Routes."""

from fastapi import APIRouter
import redis
import os

router = APIRouter()

def _get_redis():
    try:
        url = os.getenv("REDIS_URL", "redis://localhost:6379")
        return redis.from_url(url, decode_responses=True)
    except Exception:
        return None

@router.get("")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents": "ready"
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check with actual connectivity verification."""
    checks = {
        "redis": "unhealthy",
        "agents": "loaded"
    }

    # Check Redis
    try:
        r = _get_redis()
        if r:
            r.ping()
            checks["redis"] = "connected"
    except Exception as e:
        checks["redis"] = f"error: {str(e)[:30]}"

    unhealthy = [k for k, v in checks.items() if v not in ("connected", "loaded")]
    status = "ready" if not unhealthy else "degraded"

    return {
        "status": status,
        "checks": checks
    }