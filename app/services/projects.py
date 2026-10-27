from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.permissions import require_project_role


def create_project(db: Session, data: ProjectCreate, owner_id: UUID) -> Project:
    project = Project()
    project.name = data.name
    project.description = data.description
    project.owner_id = owner_id

    try:
        db.add(project)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.refresh(project)

    return project


def get_project(db: Session, project_id: UUID, user_id: UUID) -> Project | None:
    role = require_project_role(db, project_id, user_id, ["owner", "editor", "viewer"])
    if role is None:
        return
    project = db.get(Project, project_id)

    if project is None:
        return None

    return project


def list_projects(db: Session, user_id: UUID) -> list[Project]:
    member_project_ids = select(ProjectMember.project_id).where(
        ProjectMember.user_id == user_id
    )
    data = db.scalars(
        select(Project).where(
            or_(Project.owner_id == user_id, Project.id.in_(member_project_ids))
        )
    ).all()
    return list(data)


def update_project(
    db: Session, user_id: UUID, project_id: UUID, data: ProjectUpdate
) -> Project | None:
    role = require_project_role(db, project_id, user_id, ["owner"])
    if role is None:
        return
    project = get_project(db, project_id, user_id)

    if project is None:
        return None

    changes = data.model_dump(exclude_unset=True)

    if changes == {}:
        return project

    for key, value in changes.items():
        setattr(project, key, value)

    project.updated_at = datetime.now(UTC)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.refresh(project)

    return project


def delete_project(db: Session, user_id: UUID, project_id: UUID) -> bool:
    role = require_project_role(db, project_id, user_id, ["owner"])
    if role is None:
        return False
    project = get_project(db, project_id, user_id)

    if project is None:
        return False

    try:
        db.delete(project)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        return True
