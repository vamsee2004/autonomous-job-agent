from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.candidate import router as candidate_router
from app.api.jobs import router as jobs_router
from app.api.outreach import router as outreach_router

from app.database.connection import Base, engine

from app.models.job import Job
from app.models.application import Application
from app.models.pipeline_run import PipelineRun
from app.models.application_audit import ApplicationAudit
from app.models.outreach import Outreach
from app.models.application_feedback import ApplicationFeedback

from app.services.scheduler import (
    start_scheduler,
    stop_scheduler
)

from app.services.config_validator import (
    validate_configuration
)


# ---------------------------------------------------------
# Project directories
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"

(DATA_DIRECTORY / "resumes").mkdir(
    parents=True,
    exist_ok=True
)

(DATA_DIRECTORY / "cover_letters").mkdir(
    parents=True,
    exist_ok=True
)

(DATA_DIRECTORY / "logs").mkdir(
    parents=True,
    exist_ok=True
)


# ---------------------------------------------------------
# Database initialization
# ---------------------------------------------------------

Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Autonomous Job Automation Agent",
    description=(
        "AI-powered job search and "
        "application automation system"
    ),
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# API routers
# ---------------------------------------------------------

app.include_router(candidate_router)
app.include_router(jobs_router)
app.include_router(outreach_router)


# ---------------------------------------------------------
# Application startup
# ---------------------------------------------------------

@app.on_event("startup")
def startup_event():

    configuration = validate_configuration()

    if not configuration["valid"]:

        print(
            "WARNING: Configuration validation "
            "found errors."
        )

        for error in configuration["errors"]:

            print(
                f"Configuration error: {error}"
            )

    start_scheduler()


# ---------------------------------------------------------
# Application shutdown
# ---------------------------------------------------------

@app.on_event("shutdown")
def shutdown_event():

    stop_scheduler()


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def home():

    return {
        "message": (
            "Autonomous Job Automation Agent "
            "is running"
        )
    }


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }