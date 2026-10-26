from pydantic import BaseModel, Field, ConfigDict, field_validator, AwareDatetime
from uuid import UUID
from datetime import datetime
from typing import Literal


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(max_length=5000, default=None)
    status: Literal["todo", "in_progress", "done"] = Field(default="todo")
    priority: Literal["low", "medium", "high"] = Field(default="medium")
    assignee_id: UUID | None = Field(default=None)
    due_at: AwareDatetime | None = Field(default=None)

    @field_validator("title", mode="before")
    def check_title(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Название не может быть None")
        if not isinstance(value, str):
            raise ValueError("Название должно быть строкой")

        return value.strip()


class TaskRead(BaseModel):
    id: UUID
    project_id: UUID
    created_by: UUID
    title: str
    description: str | None
    status: Literal["todo", "in_progress", "done"]
    priority: Literal["low", "medium", "high"]
    assignee_id: UUID | None
    due_at: AwareDatetime | None
    created_at: AwareDatetime
    updated_at: AwareDatetime

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    title: str | None = Field(min_length=1, max_length=160, default=None)
    description: str | None = Field(max_length=5000, default=None)
    status: Literal["todo", "in_progress", "done"] | None = Field(default=None)
    priority: Literal["low", "medium", "high"] | None = Field(default=None)
    assignee_id: UUID | None = Field(default=None)
    due_at: AwareDatetime | None = Field(default=None)

    @field_validator("title", mode="before")
    def check_title(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Название не может быть None")
        if not isinstance(value, str):
            raise ValueError("Название должно быть строкой")

        return value.strip()

    @field_validator("status", "priority", mode="before")
    def check_status_and_priority(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Статус или приоритет не может быть None")
        if not isinstance(value, str):
            raise ValueError("Статус или приоритет должны быть строкой")

        return value


class PaginatedTasksResponse(BaseModel):
    items: list[TaskRead]
    total: int
    offset: int
    limit: int
