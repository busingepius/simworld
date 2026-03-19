import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Float, UUID, ForeignKey, Text, DateTime

from models.base import TenantBase

class CalibrationEntry(TenantBase):
    __tablename__ = "calibration_entries"

    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    world_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("worlds.id", ondelete="CASCADE"), nullable=False)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    
    prediction_text: Mapped[str] = mapped_column(Text, nullable=False)
    outcome_text: Mapped[str] = mapped_column(Text, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
