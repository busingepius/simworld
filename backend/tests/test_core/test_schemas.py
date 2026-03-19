import pytest
import uuid
from datetime import datetime
from pydantic import ValidationError

from schemas.world import WorldCreate, WorldResponse
from schemas.agent import AgentPersonaCreate
from schemas.simulation import SimulationRunCreate
from schemas.scenario import ScenarioCreate

def test_world_schemas():
    # Valid
    world = WorldCreate(name="Earth", domain="Politics")
    assert world.name == "Earth"
    
    # Missing required field
    with pytest.raises(ValidationError):
        WorldCreate(name="Earth")

def test_simulation_run_schema_limits():
    # Valid
    sim = SimulationRunCreate(rounds=50)
    assert sim.rounds == 50
    
    # Exceeds max rounds (le=100)
    with pytest.raises(ValidationError):
        SimulationRunCreate(rounds=150)
        
    # Below min rounds (ge=1)
    with pytest.raises(ValidationError):
        SimulationRunCreate(rounds=0)

def test_scenario_schema_limits():
    # Valid strength
    scenario = ScenarioCreate(description="Event", strength=3.0)
    assert scenario.strength == 3.0
    
    # Exceeds max strength (le=5.0)
    with pytest.raises(ValidationError):
        ScenarioCreate(description="Event", strength=10.0)
