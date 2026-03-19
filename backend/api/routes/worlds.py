import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_org, get_db
from models.organisation import Organisation
from schemas.world import WorldCreate, WorldResponse
from core.exceptions import WorldNotFoundError
from core import crud

router = APIRouter()

@router.get("/", response_model=List[WorldResponse])
async def list_worlds(
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    worlds = await crud.get_worlds(db, org.id)
    return worlds

@router.post("/", response_model=WorldResponse, status_code=status.HTTP_201_CREATED)
async def create_world(
    world_in: WorldCreate,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.create_world(
        db, 
        org_id=org.id, 
        name=world_in.name, 
        domain=world_in.domain, 
        config=world_in.config
    )
    return world

@router.get("/{world_id}", response_model=WorldResponse)
async def get_world(
    world_id: uuid.UUID,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})
    return world
