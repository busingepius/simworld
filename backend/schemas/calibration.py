import uuid
from pydantic import BaseModel, Field
from datetime import datetime

class CalibrationEntryBase(BaseModel):
    prediction_text: str
    outcome_text: str
    match_score: float = Field(..., ge=0.0, le=1.0)

class CalibrationEntryCreate(CalibrationEntryBase):
    report_id: uuid.UUID

class CalibrationEntryResponse(CalibrationEntryBase):
    id: uuid.UUID
    world_id: uuid.UUID
    org_id: uuid.UUID
    report_id: uuid.UUID
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
