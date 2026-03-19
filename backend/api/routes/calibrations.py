import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_org, get_db
from models.organisation import Organisation
from schemas.calibration import CalibrationEntryCreate, CalibrationEntryResponse
from core.exceptions import WorldNotFoundError
from core import crud

router = APIRouter()

@router.post("/{world_id}/calibrations", response_model=CalibrationEntryResponse)
async def create_calibration(
    world_id: uuid.UUID,
    cal_in: CalibrationEntryCreate,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})
        
    cal = await crud.create_calibration(
        db,
        org_id=org.id,
        world_id=world_id,
        report_id=cal_in.report_id,
        prediction_text=cal_in.prediction_text,
        outcome_text=cal_in.outcome_text,
        match_score=cal_in.match_score
    )
    return cal

@router.get("/{world_id}/calibrations", response_model=List[CalibrationEntryResponse])
async def list_calibrations(
    world_id: uuid.UUID,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})
        
    cals = await crud.get_calibrations(db, world_id, org.id)
    return cals
