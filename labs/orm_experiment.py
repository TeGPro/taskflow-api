from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.project import Project

# with SessionLocal() as session:
#     user = User(
#         email="orm_commit@example.com",
#         display_name="Учебный пользователь",
#         password_hash="training_hash",
#     )
#     print("До flush:", user.id)
#     session.add(user)
#     session.flush()

#     print("После flush:", user.id)

#     session.commit()

with SessionLocal() as session:
    data = session.scalar(select(Project).where(Project.name == "Учебная платформа"))
    if data is None:
        print("Проект не найден")
    else:
        for task in data.tasks:
            print(task.title)
