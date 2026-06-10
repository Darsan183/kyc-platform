"""Test configuration."""

import pytest
import asyncio


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "date_of_birth": "1990-01-15",
        "country": "US",
        "documents": [
            {"type": "passport", "confidence": 0.9},
            {"type": "utility_bill", "confidence": 0.85}
        ],
        "scores": {
            "document": 100,
            "identity": 95,
            "aml": 100,
            "media": 90,
            "compliance": 100
        }
    }