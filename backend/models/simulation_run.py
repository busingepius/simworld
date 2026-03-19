import uuid
from typing import Any, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, UUID, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from models.base import TenantBase

class SimulationRun(TenantBase):
    __tablename__ = "simulation_runs"

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    world_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    scenario_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("scenarios.id", ondelete="SET NULL"), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    platform_config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    llm_call_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
