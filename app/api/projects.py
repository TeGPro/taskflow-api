from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.projects import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)

router = APIRouter(prefix="/projects")

TEST_USER_ID = UUID("3931796b-ebcd-48c0-963b-272fdc7f2d13")


@router.post("", response_model=ProjectRead, status_code=201)
def projects_post(data: ProjectCreate, db: Session = Depends(get_db)):
    return create_project(db, data, TEST_USER_ID)


@router.get("/{project_id}", response_model=ProjectRead)
def project_get(project_id: UUID, db: Session = Depends(get_db)):
    project = get_project(db, project_id, TEST_USER_ID)
    if project is None:
        raise HTTPException(404, detail="Project not found")
    return project


@router.get("", response_model=list[ProjectRead])
def projects_get(db: Session = Depends(get_db)):
    return list_projects(db, TEST_USER_ID)


@router.patch("/{project_id}", response_model=ProjectRead, status_code=200)
def projects_patch(
    project_id: UUID, data: ProjectUpdate, db: Session = Depends(get_db)
):
    project = update_project(db, TEST_USER_ID, project_id, data)
    if project is None:
        raise HTTPException(status_code=404)
    return project


@router.delete("/{project_id}", status_code=204)
def project_delete(project_id: UUID, db: Session = Depends(get_db)):
    status = delete_project(db, TEST_USER_ID, project_id)

    if status is False:
        raise HTTPException(status_code=404)

    return Response(status_code=204)
