from psycopg.errors import UniqueViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin


def create_user(db: Session, data: UserCreate) -> User | None:
    email = data.email.lower()

    existing_user = db.scalar(select(User).where(User.email == email))

    if existing_user is not None:
        raise ValueError("Email уже занят")
    user = User()

    user.email = email
    user.display_name = data.display_name
    user.password_hash = hash_password(data.password)

    try:
        db.add(user)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if (
            isinstance(e.orig, UniqueViolation)
            and e.orig.diag.constraint_name == "uq_users_email"
        ):
            raise ValueError("Email уже занят")
        raise
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.refresh(user)

    return user


def authenticate_user(db: Session, data: UserLogin) -> User | None:
    email = data.email.lower()
    user = db.scalar(select(User).where(User.email == email))

    if user is None:
        return None

    correct_password = verify_password(data.password, user.password_hash)

    if correct_password is False:
        return None
    if user.is_active is False:
        return None
    return user
