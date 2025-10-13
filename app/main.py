from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.v1 import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Add startup tasks
    yield
    # TODO: Add shutdown tasks


app = FastAPI(debug=True, lifespan=lifespan)
app.include_router(health.router, prefix="/api/v1", tags=["health"])
