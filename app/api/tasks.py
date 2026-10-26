from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate, PaginatedTasksResponse
from app.services.tasks import (
    create_task,
    get_task,
    update_task,
    delete_task,
    list_project_tasks,
)
from typing import Literal


router = APIRouter()

TEST_USER_ID = UUID("3931796b-ebcd-48c0-963b-272fdc7f2d13")


@router.post("/projects/{project_id}/tasks", status_code=201, response_model=TaskRead)
def project_tasks(project_id: UUID, data: TaskCreate, db: Session = Depends(get_db)):
    try:
        task = create_task(db, data, project_id, TEST_USER_ID)
        if task is None:
            raise HTTPException(status_code=404)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return task


@router.get("/tasks/{task_id}", response_model=TaskRead)
def task_get(task_id: UUID, db: Session = Depends(get_db)):
    task = get_task(db, task_id, TEST_USER_ID)
    if task is None:
        raise HTTPException(status_code=404)
    return task


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def tasks_path(task_id: UUID, data: TaskUpdate, db: Session = Depends(get_db)):
    try:
        task = update_task(db, task_id, TEST_USER_ID, data)
        if task is None:
            raise HTTPException(status_code=404)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def tasks_delete(task_id: UUID, db: Session = Depends(get_db)):
    deleted = delete_task(db, task_id, TEST_USER_ID)
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
):
    tasks = list_project_tasks(db, project_id, TEST_USER_ID, limit, offset, status)
    if tasks is None:
        raise HTTPException(status_code=404)
    return tasks
