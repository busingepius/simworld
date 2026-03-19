import uuid
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class ScenarioBase(BaseModel):
    description: str
    strength: float = Field(default=1.0, ge=0.1, le=5.0)
    target_agent_ids: List[uuid.UUID] = Field(default_factory=list)

class ScenarioCreate(ScenarioBase):
    pass

class ScenarioResponse(ScenarioBase):
    id: uuid.UUID
    world_id: uuid.UUID
    org_id: uuid.UUID
    linked_run_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
