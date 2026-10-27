from uuid import UUID

from psycopg.errors import UniqueViolation
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember
from app.models.task import Task
from app.models.user import User
from app.schemas.project_member import ProjectMemberCreate, ProjectMemberUpdate
from app.services.permissions import require_project_role
from app.services.projects import get_project


class UserNotFoundError(ValueError):
    pass


class MemberAlreadyExistsError(ValueError):
    pass


def add_project_member(
    db: Session, project_id: UUID, user_id: UUID, data: ProjectMemberCreate
):
    role = require_project_role(db, project_id, user_id, ["owner"])
    if role is None:
        return
    project = get_project(db, project_id, user_id)

    if project is None:
        return

    email = data.email.lower()

    invited_user = db.scalar(select(User).where(User.email == email))

    if invited_user is None:
        raise UserNotFoundError("Пользователь не найден")
    if invited_user.id == project.owner_id:
        raise MemberAlreadyExistsError("Владелец уже имеет доступ к проекту")

    existing_member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.user_id == invited_user.id,
            ProjectMember.project_id == project_id,
        )
    )

    if existing_member is not None:
        raise MemberAlreadyExistsError("Участник уже добавлен")

    project_member = ProjectMember()
    project_member.project_id = project_id
    project_member.user_id = invited_user.id
    project_member.role = data.role

    try:
        db.add(project_member)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if (
            isinstance(e.orig, UniqueViolation)
            and e.orig.diag.constraint_name == "pk_project_members"
        ):
            raise MemberAlreadyExistsError("Участник уже добавлен")
        raise
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.refresh(project_member)

    return project_member


def list_project_members(db: Session, project_id: UUID, user_id: UUID):
    role = require_project_role(db, project_id, user_id, ["owner", "editor", "viewer"])
    if role is None:
        return

    stmt = (
        select(ProjectMember.user_id, User.email, User.display_name, ProjectMember.role)
        .join(User, ProjectMember.user_id == User.id)
        .where(ProjectMember.project_id == project_id)
    )
    members = db.execute(stmt).mappings().all()

    return members


def update_project_member(
    db: Session,
    project_id: UUID,
    user_id: UUID,
    member_user_id: UUID,
    data: ProjectMemberUpdate,
):
    role = require_project_role(db, project_id, user_id, ["owner"])
    if role is None:
        return

    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_user_id,
        )
    )
    if member is None:
        return

    member.role = data.role
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.refresh(member)

    return member


def delete_project_member(
    db: Session, project_id: UUID, user_id: UUID, member_user_id: UUID
) -> bool:
    role = require_project_role(db, project_id, user_id, ["owner"])
    if role is None:
        return False

    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_user_id,
        )
    )
    if member is None:
        return False

    try:
        db.execute(
            update(Task)
            .where(Task.project_id == project_id, Task.assignee_id == member_user_id)
            .values(assignee_id=None)
        )
        db.delete(member)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        return True
