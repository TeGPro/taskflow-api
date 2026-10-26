from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(max_length=2000, default=None)

    @field_validator("name", mode="before")
    def check_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Имя не может быть None")
        if not isinstance(value, str):
            raise ValueError("Имя должно быть строкой")

        return value.strip()


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

    @field_validator("name", mode="before")
    def check_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Имя не может быть None")
        if not isinstance(value, str):
            raise ValueError("Имя должно быть строкой")

        return value.strip()
