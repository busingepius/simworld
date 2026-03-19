import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_org, get_db
from models.organisation import Organisation
from schemas.agent import AgentPersonaResponse
from core.agent_factory import generate_personas_from_graph
from core.exceptions import WorldNotFoundError
from core import crud

router = APIRouter()

@router.get("/{world_id}/agents", response_model=List[AgentPersonaResponse])
async def list_agents(
    world_id: uuid.UUID,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})
        
    agents = await crud.get_agents(db, world_id, org.id)
    return agents

@router.post("/{world_id}/agents/generate")
async def generate_agents(
    world_id: uuid.UUID,
    count: int = 5,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})
        
    personas = await generate_personas_from_graph(world_id, org.id, count=count)
    created_count = await crud.save_generated_agents(db, org.id, world_id, personas)
    
    return {"status": "generated", "count": created_count}
