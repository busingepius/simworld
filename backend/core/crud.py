import uuid
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from models.world import World
from models.agent_persona import AgentPersona
from models.simulation_run import SimulationRun
from models.scenario import Scenario
from models.report import Report
from models.calibration_entry import CalibrationEntry
from models.seed_material import SeedMaterial

async def get_worlds(db: AsyncSession, org_id: uuid.UUID) -> List[World]:
    result = await db.execute(select(World).where(World.org_id == org_id))
    return list(result.scalars().all())

async def get_world(db: AsyncSession, world_id: uuid.UUID, org_id: uuid.UUID) -> Optional[World]:
    result = await db.execute(select(World).where(World.id == world_id, World.org_id == org_id))
    return result.scalars().first()

async def create_world(db: AsyncSession, org_id: uuid.UUID, name: str, domain: str, config: dict) -> World:
    world = World(org_id=org_id, name=name, domain=domain, config=config)
    db.add(world)
    await db.commit()
    await db.refresh(world)
    return world

async def create_seed_material(db: AsyncSession, org_id: uuid.UUID, world_id: uuid.UUID, filename: str, file_type: str, storage_path: str) -> SeedMaterial:
    material = SeedMaterial(org_id=org_id, world_id=world_id, filename=filename, file_type=file_type, storage_path=storage_path)
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material

async def get_agents(db: AsyncSession, world_id: uuid.UUID, org_id: uuid.UUID) -> List[AgentPersona]:
    result = await db.execute(select(AgentPersona).where(AgentPersona.world_id == world_id, AgentPersona.org_id == org_id))
    return list(result.scalars().all())

async def save_generated_agents(db: AsyncSession, org_id: uuid.UUID, world_id: uuid.UUID, personas: List[Any]) -> int:
    created = 0
    for p in personas:
        agent = AgentPersona(
            org_id=org_id,
            world_id=world_id,
            name=p.name,
            personality=p.personality.model_dump(),
            stance=[s.model_dump() for s in p.stances],
            influence_score=p.influence_score
        )
        db.add(agent)
        created += 1
    await db.commit()
    return created

async def create_simulation_run(db: AsyncSession, org_id: uuid.UUID, world_id: uuid.UUID, scenario_id: Optional[uuid.UUID], rounds: int, platform_config: dict) -> SimulationRun:
    run = SimulationRun(org_id=org_id, world_id=world_id, scenario_id=scenario_id, rounds=rounds, platform_config=platform_config)
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run

async def get_simulation_runs(db: AsyncSession, world_id: uuid.UUID, org_id: uuid.UUID) -> List[SimulationRun]:
    result = await db.execute(select(SimulationRun).where(SimulationRun.world_id == world_id, SimulationRun.org_id == org_id))
    return list(result.scalars().all())

async def create_scenario(db: AsyncSession, org_id: uuid.UUID, world_id: uuid.UUID, description: str, strength: float, target_agent_ids: List[uuid.UUID]) -> Scenario:
    scenario = Scenario(org_id=org_id, world_id=world_id, description=description, strength=strength, target_agent_ids=target_agent_ids)
    db.add(scenario)
    await db.commit()
    await db.refresh(scenario)
    return scenario

async def get_scenarios(db: AsyncSession, world_id: uuid.UUID, org_id: uuid.UUID) -> List[Scenario]:
    result = await db.execute(select(Scenario).where(Scenario.world_id == world_id, Scenario.org_id == org_id))
    return list(result.scalars().all())

async def get_reports(db: AsyncSession, world_id: uuid.UUID, org_id: uuid.UUID) -> List[Report]:
    result = await db.execute(select(Report).where(Report.world_id == world_id, Report.org_id == org_id))
    return list(result.scalars().all())

async def create_calibration(db: AsyncSession, org_id: uuid.UUID, world_id: uuid.UUID, report_id: uuid.UUID, prediction_text: str, outcome_text: str, match_score: float) -> CalibrationEntry:
    cal = CalibrationEntry(org_id=org_id, world_id=world_id, report_id=report_id, prediction_text=prediction_text, outcome_text=outcome_text, match_score=match_score)
    db.add(cal)
    await db.commit()
    await db.refresh(cal)
    return cal

async def get_calibrations(db: AsyncSession, world_id: uuid.UUID, org_id: uuid.UUID) -> List[CalibrationEntry]:
    result = await db.execute(select(CalibrationEntry).where(CalibrationEntry.world_id == world_id, CalibrationEntry.org_id == org_id))
    return list(result.scalars().all())
