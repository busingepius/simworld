import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class WorldBase(BaseModel):
    name: str
    domain: str
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)

class WorldCreate(WorldBase):
    pass

class WorldUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class WorldResponse(WorldBase):
    id: uuid.UUID
    org_id: uuid.UUID
    status: str
    agent_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
