from fastapi import FastAPI

from app.core.logging import setup_logging
from app.api.v1.routers.auth import router as auth_router

setup_logging()

app = FastAPI()

app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
