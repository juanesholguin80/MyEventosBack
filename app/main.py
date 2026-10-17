from fastapi import FastAPI

from app.core.logging import setup_logging
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.events import router as events_router
from app.api.v1.routers.registrations import router as registrations_router
from app.api.v1.routers.sessions import router as sessions_router
from app.api.v1.routers.speakers import router as speakers_router
from app.api.v1.routers.users import router as users_router, profile_router

setup_logging()

app = FastAPI()

app.include_router(auth_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(speakers_router, prefix="/api/v1")
app.include_router(registrations_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
