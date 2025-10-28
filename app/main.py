from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.db.base import metadata
from app.db.session import engine

from .api.v1 import activity, food, health, user, water


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Add startup tasks
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield
    # TODO: Add shutdown tasks


app = FastAPI(debug=True, lifespan=lifespan)

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health.router, tags=["health"])
api_v1_router.include_router(user.router, tags=["user"])
api_v1_router.include_router(water.router, tags=["water"])
api_v1_router.include_router(food.router, tags=["food"])
api_v1_router.include_router(activity.router, tags=["activity"])

app.include_router(api_v1_router)
