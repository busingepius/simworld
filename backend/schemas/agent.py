import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class AgentPersonaBase(BaseModel):
    name: str
    personality: Dict[str, Any]
    stance: Dict[str, Any]
    influence_score: float

class AgentPersonaCreate(AgentPersonaBase):
    pass

class AgentPersonaUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[Dict[str, Any]] = None
    stance: Optional[Dict[str, Any]] = None
    influence_score: Optional[float] = None
    is_active: Optional[bool] = None

class AgentPersonaResponse(AgentPersonaBase):
    id: uuid.UUID
    world_id: uuid.UUID
    org_id: uuid.UUID
    zep_user_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
