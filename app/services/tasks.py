from datetime import datetime, UTC
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from sqlalchemy import select
from app.services.projects import get_project


def create_task(
    db: Session, data: TaskCreate, project_id: UUID, user_id: UUID
) -> Task | None:
    project = get_project(db, project_id, user_id)
    if project is None:
        return None
    if data.assignee_id is not None and data.assignee_id != project.owner_id:
        member = db.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == data.assignee_id,
            )
        )
        if member is None:
            raise ValueError("Исполнитель не является участником проекта")

    task = Task()

    task.title = data.title
    task.description = data.description
    task.priority = data.priority
    task.status = data.status
    task.assignee_id = data.assignee_id
    task.due_at = data.due_at
    task.project_id = project_id
    task.created_by = user_id

    try:
        db.add(task)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.refresh(task)

    return task


def get_task(db: Session, task_id: UUID, user_id: UUID) -> Task | None:
    task = db.get(Task, task_id)

    if task is None:
        return None

    project = get_project(db, task.project_id, user_id)

    if project is None:
        return None

    return task


def update_task(
    db: Session, task_id: UUID, user_id: UUID, data: TaskUpdate
) -> Task | None:
    task = get_task(db, task_id, user_id)
    if task is None:
        return None
    changes = data.model_dump(exclude_unset=True)
    if changes == {}:
        return task

    if "assignee_id" in changes and changes["assignee_id"] is not None:
        assignee_id = changes["assignee_id"]
        project = get_project(db, task.project_id, user_id)
        if project is None:
            return None
        if project.owner_id != assignee_id:
            member = db.scalar(
                select(ProjectMember).where(
                    ProjectMember.project_id == project.id,
                    ProjectMember.user_id == assignee_id,
                )
            )
            if member is None:
                raise ValueError("Исполнитель не является участником проекта")

    for key, value in changes.items():
        setattr(task, key, value)

    task.updated_at = datetime.now(UTC)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.refresh(task)

    return task


def delete_task(db: Session, task_id: UUID, user_id: UUID) -> bool:
    task = get_task(db, task_id, user_id)
    if task is None:
        return False
    try:
        db.delete(task)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        return True
