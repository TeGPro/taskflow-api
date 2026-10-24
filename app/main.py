from fastapi import FastAPI
from app.api.projects import router
from app.api.tasks import router as task_router

app = FastAPI()
app.include_router(router, prefix="/api/v1")
app.include_router(task_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
