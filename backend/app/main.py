from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.db import create_db_and_tables
from app.jobs.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    if settings.scheduler_enabled:
        start_scheduler()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
