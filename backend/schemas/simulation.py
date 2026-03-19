import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class SimulationRunBase(BaseModel):
    scenario_id: Optional[uuid.UUID] = None
    rounds: int = Field(default=5, ge=1, le=100)
    platform_config: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SimulationRunCreate(SimulationRunBase):
    pass

class SimulationRunResponse(SimulationRunBase):
    id: uuid.UUID
    world_id: uuid.UUID
    org_id: uuid.UUID
    status: str
    llm_call_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
