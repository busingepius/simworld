import uuid
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

class ReportSectionSchema(BaseModel):
    title: str
    content: str

class ReportBase(BaseModel):
    summary: str
    sections: List[ReportSectionSchema]
    confidence_score: float

class ReportResponse(ReportBase):
    id: uuid.UUID
    world_id: uuid.UUID
    run_id: uuid.UUID
    org_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
