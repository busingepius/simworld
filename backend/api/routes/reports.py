import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_org, get_db
from models.organisation import Organisation
from models.report import Report
from schemas.report import ReportResponse
from core.exceptions import WorldNotFoundError
from core import crud

router = APIRouter()

@router.get("/{world_id}/reports", response_model=List[ReportResponse])
async def list_reports(
    world_id: uuid.UUID,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})
        
    reports = await crud.get_reports(db, world_id, org.id)
    return reports

@router.get("/{world_id}/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    world_id: uuid.UUID,
    report_id: uuid.UUID,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    report = await db.get(Report, report_id)
    if not report or report.org_id != org.id or report.world_id != world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
