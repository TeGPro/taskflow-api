from datetime import datetime
from uuid import UUID
from sqlalchemy import ForeignKey, String, DateTime, func, CheckConstraint
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint("role IN ('editor', 'viewer')", name="ck_project_members_role"),
    )
