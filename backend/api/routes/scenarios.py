import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_org, get_db
from models.organisation import Organisation
from schemas.scenario import ScenarioCreate, ScenarioResponse
from core.exceptions import WorldNotFoundError
from core import crud

router = APIRouter()

@router.post("/{world_id}/scenarios", response_model=ScenarioResponse)
async def create_scenario(
    world_id: uuid.UUID,
    scenario_in: ScenarioCreate,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})
        
    scenario = await crud.create_scenario(
        db,
        org_id=org.id,
        world_id=world_id,
        description=scenario_in.description,
        strength=scenario_in.strength,
        target_agent_ids=scenario_in.target_agent_ids
    )
    return scenario

@router.get("/{world_id}/scenarios", response_model=List[ScenarioResponse])
async def list_scenarios(
    world_id: uuid.UUID,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})
        
    scenarios = await crud.get_scenarios(db, world_id, org.id)
    return scenarios
