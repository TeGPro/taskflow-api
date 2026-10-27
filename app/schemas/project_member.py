from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr


class ProjectMemberCreate(BaseModel):
    email: EmailStr
    role: Literal["editor", "viewer"]


class ProjectMemberRead(BaseModel):
    project_id: UUID
    user_id: UUID
    role: Literal["editor", "viewer"]
    joined_at: AwareDatetime

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberListItem(BaseModel):
    user_id: UUID
    email: EmailStr
    display_name: str
    role: Literal["editor", "viewer"]


class ProjectMemberUpdate(BaseModel):
    role: Literal["editor", "viewer"]
