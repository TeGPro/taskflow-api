from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


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
    project = db.get(Project, project_id)

    if project is None:
        return None

    if user_id == project.owner_id:
        return project

    return None


def list_projects(db: Session, user_id: UUID) -> list[Project]:
    data = db.scalars(select(Project).where(Project.owner_id == user_id)).all()
    return list(data)


def update_project(
    db: Session, user_id: UUID, project_id: UUID, data: ProjectUpdate
) -> Project | None:
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
