import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_org, get_db
from models.organisation import Organisation
from schemas.simulation import SimulationRunCreate, SimulationRunResponse
from core.exceptions import WorldNotFoundError
from core import crud
from workers.celery_app import celery

router = APIRouter()

@router.post("/{world_id}/runs", response_model=SimulationRunResponse)
async def create_simulation_run(
    world_id: uuid.UUID,
    sim_in: SimulationRunCreate,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})
        
    run = await crud.create_simulation_run(
        db,
        org_id=org.id,
        world_id=world_id,
        scenario_id=sim_in.scenario_id,
        rounds=sim_in.rounds,
        platform_config=sim_in.platform_config or {}
    )
    
    celery.send_task("workers.simulation.run_simulation_task", args=[str(run.id)])
    
    return run

@router.get("/{world_id}/runs", response_model=List[SimulationRunResponse])
async def list_simulation_runs(
    world_id: uuid.UUID,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})
        
    runs = await crud.get_simulation_runs(db, world_id, org.id)
    return runs
