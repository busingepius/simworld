from sqlalchemy import inspect
from models.base import Base

def test_models_exist():
    # Simple test to ensure all models are registered with Base metadata
    tables = Base.metadata.tables.keys()
    
    expected_tables = {
        "organisations",
        "worlds",
        "seed_materials",
        "agent_personas",
        "scenarios",
        "simulation_runs",
        "simulation_states",
        "reports",
        "calibration_entries"
    }
    
    assert expected_tables.issubset(tables)
