from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings
from app.core.database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    initialize_database(get_settings())
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="wi-Q Great Food Integration",
        summary="Consumes Great Food Ltd menu APIs and exposes scenario workflows.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app()
