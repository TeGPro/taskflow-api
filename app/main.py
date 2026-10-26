from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.tasks import router as task_router

app = FastAPI()
app.include_router(projects_router, prefix="/api/v1")
app.include_router(task_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
