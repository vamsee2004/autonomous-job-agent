from fastapi import FastAPI

from app.api.candidate import router as candidate_router
from app.api.jobs import router as jobs_router

from app.database.connection import Base, engine

from app.models.job import Job
from app.models.application import Application
from app.models.pipeline_run import PipelineRun

from app.services.scheduler import (
    start_scheduler,
    stop_scheduler
)


# Create all database tables
Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Autonomous Job Automation Agent",
    description=(
        "AI-powered job search and "
        "application automation system"
    ),
    version="1.0.0"
)


# Register API routers
app.include_router(
    candidate_router
)

app.include_router(
    jobs_router
)


@app.on_event("startup")
def startup_event():

    start_scheduler()


@app.on_event("shutdown")
def shutdown_event():

    stop_scheduler()


@app.get("/")
def home():

    return {
        "message": (
            "Autonomous Job Automation Agent "
            "is running"
        )
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }