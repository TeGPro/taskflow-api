from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberListItem,
    ProjectMemberRead,
    ProjectMemberUpdate,
)
from app.services.permissions import ProjectPermissionError
from app.services.project_members import (
    MemberAlreadyExistsError,
    UserNotFoundError,
    add_project_member,
    delete_project_member,
    list_project_members,
    update_project_member,
)
from app.services.projects import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)

router = APIRouter(prefix="/projects")


@router.post("", response_model=ProjectRead, status_code=201)
def projects_post(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_project(db, data, current_user.id)


@router.get("/{project_id}", response_model=ProjectRead)
def project_get(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = get_project(db, project_id, current_user.id)
    if project is None:
        raise HTTPException(404, detail="Project not found")
    return project


@router.get("", response_model=list[ProjectRead])
def projects_get(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return list_projects(db, current_user.id)


@router.patch("/{project_id}", response_model=ProjectRead, status_code=200)
def projects_patch(
    project_id: UUID,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        project = update_project(db, current_user.id, project_id, data)
    except ProjectPermissionError as e:
        raise HTTPException(status_code=403, detail=(str(e)))

    if project is None:
        raise HTTPException(status_code=404)
    return project


@router.delete("/{project_id}", status_code=204)
def project_delete(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        status = delete_project(db, current_user.id, project_id)
    except ProjectPermissionError:
        raise HTTPException(status_code=403)
    if status is False:
        raise HTTPException(status_code=404)

    return Response(status_code=204)


@router.post("/{project_id}/members", status_code=201, response_model=ProjectMemberRead)
def project_members_add(
    project_id: UUID,
    data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        member = add_project_member(db, project_id, current_user.id, data)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=(str(e)))
    except MemberAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=(str(e)))
    except ProjectPermissionError:
        raise HTTPException(status_code=403)

    if member is None:
        raise HTTPException(status_code=404)

    return member


@router.get("/{project_id}/members", response_model=list[ProjectMemberListItem])
def project_members_list(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    members = list_project_members(db, project_id, current_user.id)
    if members is None:
        raise HTTPException(status_code=404)
    return members


@router.patch(
    "/{project_id}/members/{member_user_id}", response_model=ProjectMemberRead
)
def update_member_role(
    project_id: UUID,
    member_user_id: UUID,
    data: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        member = update_project_member(
            db, project_id, current_user.id, member_user_id, data
        )
    except ProjectPermissionError:
        raise HTTPException(status_code=403)

    if member is None:
        raise HTTPException(status_code=404)

    return member


@router.delete("/{project_id}/members/{member_user_id}", status_code=204)
def delete_member(
    project_id: UUID,
    member_user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted = delete_project_member(db, project_id, current_user.id, member_user_id)
    except ProjectPermissionError:
        raise HTTPException(status_code=403)

    if deleted is False:
        raise HTTPException(status_code=404)

    return Response(status_code=204)
