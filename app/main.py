from fastapi import FastAPI
from app.api.projects import router

app = FastAPI()
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
