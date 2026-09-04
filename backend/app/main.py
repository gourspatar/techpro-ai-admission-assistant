from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import engine, get_db
from app.api.routes.courses import router as courses_router
from app.api.routes.lead import router as leads_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(courses_router)
app.include_router(leads_router)

@app.get("/health")
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "environment": settings.environment,
        "database": "connected",
    }

@app.get("/db-test")
def database_test(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {
        "database": "connected",
        "result": result.scalar(),
    }