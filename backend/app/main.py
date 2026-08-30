from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.get("/health")
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "environment": settings.environment,
        "database": "connected",
    }