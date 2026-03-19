import uuid
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY

from models.base import TenantBase

class Scenario(TenantBase):
    __tablename__ = "scenarios"

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    world_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    
    description: Mapped[str] = mapped_column(String, nullable=False)
    strength: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    target_agent_ids: Mapped[list[uuid.UUID]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)
    linked_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("simulation_runs.id", ondelete="SET NULL"), nullable=True)
