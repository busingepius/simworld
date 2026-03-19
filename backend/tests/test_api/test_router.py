import pytest
from fastapi.testclient import TestClient
from fastapi import APIRouter, Request
import json

from api.main import app
from core.exceptions import WorldNotFoundError, SimulationLimitExceededError

mock_router = APIRouter()

@mock_router.get("/test/world-not-found")
async def trigger_world_not_found():
    raise WorldNotFoundError("The requested world was not found", {"world_id": "test_id"})

@mock_router.get("/test/simulation-limit")
async def trigger_sim_limit():
    raise SimulationLimitExceededError("Too many rounds", {"rounds": 200})

# Include test routes in the app specifically for testing
app.include_router(mock_router)

client = TestClient(app)

def test_exception_handler_world_not_found():
    response = client.get("/test/world-not-found")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "WORLD_NOT_FOUND"
    assert data["error"]["message"] == "The requested world was not found"
    assert data["error"]["detail"]["world_id"] == "test_id"

def test_exception_handler_simulation_limit():
    response = client.get("/test/simulation-limit")
    assert response.status_code == 402
    data = response.json()
    assert data["error"]["code"] == "SIMULATION_LIMIT_EXCEEDED"
