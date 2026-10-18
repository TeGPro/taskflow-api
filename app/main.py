from fastapi import FastAPI

app = FastAPI()
# app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
