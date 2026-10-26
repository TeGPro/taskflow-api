from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.project import ProjectCreate
from app.services.projects import create_project

with SessionLocal() as db:
    user = User(
        email="learner@example.com",
        display_name="Учебный пользователь",
        password_hash="training_hash",
    )

    try:
        db.add(user)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    else:
        db.refresh(user)
        user_id = user.id
        print(user_id)


with SessionLocal() as db:
    create_project(db, ProjectCreate(name="Учебная платформа"), user_id)
    print("Проект успешно создан")
