import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, UUID, ForeignKey

from models.base import TenantBase

class SeedMaterial(TenantBase):
    __tablename__ = "seed_materials"

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    world_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
