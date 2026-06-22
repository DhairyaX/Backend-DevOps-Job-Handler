from fastapi import FastAPI
from app.core.config import settings
from app.db.database import engine, Base

# Import all models here so SQLAlchemy knows about them before calling create_all
from app.models.job import Job
from app.models.transaction import Transaction
from app.models.job_summary import JobSummary

# Create all tables in the PostgreSQL database if they don't already exist
# Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

from app.routers import jobs
app.include_router(jobs.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Backend Internship Assignment API", 
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok", 
        "db_configured_for": settings.POSTGRES_SERVER,
        "redis_configured_for": settings.REDIS_HOST
    }

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)