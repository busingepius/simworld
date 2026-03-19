import uuid
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from models.base import TenantBase

class World(TenantBase):
    __tablename__ = "worlds"

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    agent_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
