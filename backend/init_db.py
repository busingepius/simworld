import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from models.base import Base
from core.config import get_settings

# Import all models so they are registered with Base.metadata
from models.organisation import Organisation
from models.world import World
from models.agent_persona import AgentPersona
from models.seed_material import SeedMaterial
from models.simulation_run import SimulationRun
from models.simulation_state import SimulationState
from models.scenario import Scenario
from models.report import Report
from models.calibration_entry import CalibrationEntry

settings = get_settings()

async def init_db():
    print("Database is managed by Alembic, bypassing direct SQLAlchemy create_all.")
    pass

if __name__ == "__main__":
    asyncio.run(init_db())
