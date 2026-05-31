"""FastAPI entry point for the sign language recognition backend."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from api.core.settings import settings
from api.routes.prediction_routes import router as prediction_router
from api.services.recognition_service import shutdown_recognition_service

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Handles API startup and shutdown lifecycle."""
    yield
    shutdown_recognition_service()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Basic health check for mobile clients and local testing."""
    return {"status": "ok"}


app.include_router(prediction_router)
