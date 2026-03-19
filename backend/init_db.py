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
    print("Creating tables via SQLAlchemy...")
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    print("Database initialization complete.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
