import uuid
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, UUID, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB

from models.base import TenantBase

class Report(TenantBase):
    __tablename__ = "reports"

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    world_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("simulation_runs.id", ondelete="CASCADE"), nullable=False)
    
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    sections: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    motif_scene: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)
