from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.task import PaginatedTasksResponse, TaskCreate, TaskRead, TaskUpdate
from app.services.permissions import ProjectPermissionError
from app.services.tasks import (
    create_task,
    delete_task,
    get_task,
    list_project_tasks,
    update_task,
)

router = APIRouter()


@router.post("/projects/{project_id}/tasks", status_code=201, response_model=TaskRead)
def project_tasks(
    project_id: UUID,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        task = create_task(db, data, project_id, current_user.id)
        if task is None:
            raise HTTPException(status_code=404)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ProjectPermissionError:
        raise HTTPException(status_code=403)
    return task


@router.get("/tasks/{task_id}", response_model=TaskRead)
def task_get(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id, current_user.id)
    if task is None:
        raise HTTPException(status_code=404)
    return task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def tasks_path(
    task_id: UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        task = update_task(db, task_id, current_user.id, data)
        if task is None:
            raise HTTPException(status_code=404)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ProjectPermissionError:
        raise HTTPException(status_code=403)
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def tasks_delete(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted = delete_task(db, task_id, current_user.id)
    except ProjectPermissionError:
        raise HTTPException(status_code=403)
    if deleted is False:
        raise HTTPException(status_code=404)
    return Response(status_code=204)


@router.get("/projects/{project_id}/tasks", response_model=PaginatedTasksResponse)
def tasks_get(
    project_id: UUID,
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Literal["todo", "in_progress", "done"] | None = None,
    sort: Literal["created_at", "due_at", "priority"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
    current_user: User = Depends(get_current_user),
):
    tasks = list_project_tasks(
        db, project_id, current_user.id, limit, offset, status, sort, order
    )
    if tasks is None:
        raise HTTPException(status_code=404)
    return tasks
