import uuid
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from models.base import TenantBase

class SimulationState(TenantBase):
    __tablename__ = "simulation_states"

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    world_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    
    opinion_distributions: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    coalitions: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    trending_topics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    raw_log_path: Mapped[str] = mapped_column(String(1024), nullable=False)
