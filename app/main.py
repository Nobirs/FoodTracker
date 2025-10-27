from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import metadata
from app.db.session import engine

from .api.v1 import food, health, user, water


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Add startup tasks
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield
    # TODO: Add shutdown tasks


app = FastAPI(debug=True, lifespan=lifespan)
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(user.router, prefix="/api/v1", tags=["user"])
app.include_router(water.router, prefix="/api/v1", tags=["water"])
app.include_router(food.router, prefix="/api/v1", tags=["food"])
