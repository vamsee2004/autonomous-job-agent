from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = PROJECT_ROOT / "data"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


# ============================================================
# CREATE DATA DIRECTORIES
# ============================================================

(DATA_DIRECTORY / "resumes").mkdir(parents=True, exist_ok=True)
(DATA_DIRECTORY / "cover_letters").mkdir(parents=True, exist_ok=True)
(DATA_DIRECTORY / "logs").mkdir(parents=True, exist_ok=True)


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Autonomous Job Automation Agent",
    description=(
        "AI-powered job search and "
        "application automation system"
    ),
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

allowed_origins = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Render frontend
    "https://autonomous-job-agent-1.onrender.com",

    # Render backend
    "https://autonomous-job-agent-069r.onrender.com",
]


frontend_url = os.getenv("FRONTEND_URL")

if frontend_url:
    frontend_url = frontend_url.rstrip("/")

    if frontend_url not in allowed_origins:
        allowed_origins.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

app.include_router(candidate_router)
app.include_router(jobs_router)
app.include_router(outreach_router)


# ============================================================
# STARTUP / SHUTDOWN
# ============================================================

@app.on_event("startup")
def startup_event():

    configuration = validate_configuration()

    if not configuration["valid"]:

        print(
            "WARNING: Configuration validation found errors."
        )

        for error in configuration["errors"]:
            print(
                f"Configuration error: {error}"
            )

    start_scheduler()


@app.on_event("shutdown")
def shutdown_event():

    stop_scheduler()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# API INFORMATION
# ============================================================

@app.get("/api")
def api_info():

    return {
        "name": "Autonomous Job Automation Agent",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "jobs": "/jobs/",
            "job_search": "/jobs/search",
            "job_discovery": "/jobs/discover",
            "applications": "/jobs/applications/"
        }
    }


# ============================================================
# SERVE REACT STATIC ASSETS
# ============================================================

if FRONTEND_DIST.exists():

    assets_directory = FRONTEND_DIST / "assets"

    if assets_directory.exists():

        app.mount(
            "/assets",
            StaticFiles(
                directory=assets_directory
            ),
            name="assets"
        )


# ============================================================
# SERVE REACT FRONTEND
# ============================================================

@app.get("/")
def serve_frontend():

    index_file = FRONTEND_DIST / "index.html"

    if index_file.exists():

        return FileResponse(index_file)

    return {
        "message": (
            "Autonomous Job Automation Agent is running, "
            "but the React frontend build was not found."
        )
    }


# ============================================================
# SPA FALLBACK
# ============================================================

@app.get("/{path:path}")
def serve_react_routes(path: str):

    # Never interfere with API routes.
    # API routers are registered before this catch-all route.

    requested_file = FRONTEND_DIST / path

    if requested_file.is_file():

        return FileResponse(requested_file)

    index_file = FRONTEND_DIST / "index.html"

    if index_file.exists():

        return FileResponse(index_file)

    return {
        "message": "Frontend build not found."
    }