import uuid
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Float, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from models.base import TenantBase

class AgentPersona(TenantBase):
    __tablename__ = "agent_personas"

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    world_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    personality: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    stance: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    influence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    zep_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
