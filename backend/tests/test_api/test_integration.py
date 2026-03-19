import pytest
import uuid
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient

from api.main import app
from api.deps import get_db, get_current_org
from models.organisation import Organisation
from core.config import get_settings

test_org_id = uuid.uuid4()
mock_org = Organisation(id=test_org_id, name="Test Org", subscription_tier="starter", api_key_hash="hash", is_active=True)

class MockResult:
    def __init__(self, data):
        self.data = data
    def scalars(self):
        return self
    def all(self):
        return self.data
    def first(self):
        return self.data[0] if self.data else None

class MockSession:
    def __init__(self):
        self.storage = {}
        
    def add(self, obj):
        import datetime
        from datetime import timezone
        
        if not hasattr(obj, "id") or not obj.id:
            obj.id = uuid.uuid4()
            
        obj.created_at = datetime.datetime.now(timezone.utc)
        obj.updated_at = datetime.datetime.now(timezone.utc)
            
        if obj.__class__.__name__ == "World":
            obj.status = "draft"
            obj.agent_count = 0
            
        if obj.__class__.__name__ == "SimulationRun":
            obj.status = "queued"
            obj.llm_call_count = 0
            
        self.storage[obj.id] = obj

    async def commit(self):
        pass

    async def refresh(self, obj):
        pass

    async def execute(self, stmt):
        # Extremely basic mock - assumes we are querying the type of the last added item
        # for our specific route tests. In a real integration test, we'd use a real PG test DB.
        items = list(self.storage.values())
        return MockResult(items)
        
    async def get(self, model, ident):
        return self.storage.get(ident)

mock_db_session = MockSession()

async def override_get_db() -> AsyncGenerator[MockSession, None]:
    yield mock_db_session

async def override_get_current_org() -> Organisation:
    return mock_org

# Override dependencies
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_org] = override_get_current_org

@pytest.fixture
def client():
    # Clear the mock DB before each test
    mock_db_session.storage = {}
    return TestClient(app)

def test_create_and_list_world(client):
    # Test Create World
    create_payload = {
        "name": "Alpha Centauri",
        "domain": "Sci-Fi",
        "config": {"gravity": "1.2g"}
    }
    response = client.post("/api/worlds/", json=create_payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Alpha Centauri"
    assert data["domain"] == "Sci-Fi"
    assert "id" in data
    
    world_id = data["id"]
    
    # Test List Worlds
    list_response = client.get("/api/worlds/")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data) == 1
    assert list_data[0]["id"] == world_id

def test_get_world_not_found(client):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/worlds/{fake_id}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "WORLD_NOT_FOUND"

def test_create_simulation_run(client):
    # Create world directly in mock db
    from models.world import World
    world = World(id=uuid.uuid4(), org_id=test_org_id, name="Earth", domain="Pol", config={})
    mock_db_session.storage[world.id] = world
    
    # Test simulation run creation
    sim_payload = {
        "rounds": 10,
        "platform_config": {"model": "gpt-4"}
    }
    
    # Mock celery send_task globally so we don't try to connect to redis
    import workers.celery_app
    workers.celery_app.celery.send_task = lambda *args, **kwargs: None
    
    sim_resp = client.post(f"/api/worlds/{world.id}/runs", json=sim_payload)
    assert sim_resp.status_code == 200
    sim_data = sim_resp.json()
    assert sim_data["rounds"] == 10
    assert sim_data["status"] == "queued"
    
def test_create_scenario(client):
    from models.world import World
    world = World(id=uuid.uuid4(), org_id=test_org_id, name="Mars", domain="Tech", config={})
    mock_db_session.storage[world.id] = world
    
    scenario_payload = {
        "description": "Meteor strike damages central dome.",
        "strength": 4.5,
        "target_agent_ids": []
    }
    
    scenario_resp = client.post(f"/api/worlds/{world.id}/scenarios", json=scenario_payload)
    assert scenario_resp.status_code == 200
    scenario_data = scenario_resp.json()
    assert scenario_data["strength"] == 4.5
    assert scenario_data["description"] == "Meteor strike damages central dome."
