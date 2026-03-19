from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean

from models.base import Base

class Organisation(Base):
    __tablename__ = "organisations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subscription_tier: Mapped[str] = mapped_column(String(50), nullable=False, default="starter")
    api_key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
