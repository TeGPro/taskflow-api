from datetime import datetime, UTC
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from sqlalchemy import select, func, case
from app.services.projects import get_project
from typing import Literal


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


def list_project_tasks(
    db: Session,
    project_id: UUID,
    user_id: UUID,
    limit: int,
    offset: int,
    status: Literal["todo", "in_progress", "done"] | None = None,
    sort: Literal["created_at", "due_at", "priority"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> dict | None:
    project = get_project(db, project_id, user_id)
    if project is None:
        return None

    stmt = select(Task).where(Task.project_id == project_id)
    if status is not None:
        stmt = stmt.where(Task.status == status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    priority_ranks = {"low": 1, "medium": 2, "high": 3}
    
    sort_fields = {
        "created_at": Task.created_at,
        "due_at": Task.due_at,
        "priority": case(priority_ranks, value = Task.priority),
    }

    sort_column = sort_fields[sort]
    if order == "desc":
        sort_expression = sort_column.desc()
    else:
        sort_expression = sort_column.asc()

    if sort == "due_at":
        sort_expression = sort_expression.nulls_last()

    stmt = stmt.order_by(sort_expression, Task.id)

    items = db.scalars(stmt.limit(limit).offset(offset)).all()

    return {"items": items, "total": total, "limit": limit, "offset": offset}
