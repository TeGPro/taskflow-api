from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(max_length=2000, default=None)


class ProjectRead(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    name: str | None = Field(min_length=1, max_length=120, default=None)
    description: str | None = Field(max_length=2000, default=None)

    @field_validator("name")
    def check_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Имя не может быть None")
        return value
