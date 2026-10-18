# это учебный прототип, данные хранятся в памяти и исчезают при перезапуске
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/playground")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    status: Literal["todo", "in_progress", "done"] = "todo"


class TaskRead(BaseModel):
    title: str
    id: UUID
    status: str


tasks_storage = {}


@router.post("/tasks", response_model=TaskRead, status_code=201)
async def tasks_post(task: TaskCreate):
    id = uuid4()
    tasks_storage[id] = {"title": task.title, "id": id, "status": task.status}
    return {"title": task.title, "id": id, "status": task.status}


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def tasks_get(task_id: UUID):
    task = tasks_storage.get(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.get("/tasks", response_model=list[TaskRead])
async def tasks_list(status: Literal["todo", "in_progress", "done"] | None = None):
    tasks = list(tasks_storage.values())
    if status is None:
        return tasks

    filtered_tasks = []
    for task in tasks:
        if task["status"] == status:
            filtered_tasks.append(task)

    return filtered_tasks
