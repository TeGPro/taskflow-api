from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember


class ProjectPermissionError(PermissionError):
    pass


def get_project_role(
    db: Session, project_id: UUID, user_id: UUID
) -> Literal["owner", "editor", "viewer"] | None:
    project = db.get(Project, project_id)
    if project is None:
        return
    if project.owner_id == user_id:
        return "owner"

    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
    )
    if member is None:
        return

    return member.role


def require_project_role(
    db: Session,
    project_id: UUID,
    user_id: UUID,
    allowed_roles: list[Literal["owner", "editor", "viewer"]],
) -> Literal["owner", "editor", "viewer"] | None:
    role = get_project_role(db, project_id, user_id)
    if role is None:
        return
    if role not in allowed_roles:
        raise ProjectPermissionError("Недостаточно прав")

    return role
