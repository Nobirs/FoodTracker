from contextlib import asynccontextmanager

from db.base import metadata
from db.session import engine
from fastapi import FastAPI

from .api.v1 import health, user

metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Add startup tasks
    yield
    # TODO: Add shutdown tasks


app = FastAPI(debug=True, lifespan=lifespan)
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(user.router, prefix="/api/v1", tags=["user"])
