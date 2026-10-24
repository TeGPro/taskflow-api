from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, String, Text, DateTime, func
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.task import Task


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task", passive_deletes=True, cascade="save-update, merge, delete"
    )
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
