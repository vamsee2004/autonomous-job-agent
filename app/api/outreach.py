from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal

from app.models.outreach import Outreach
from app.models.job import Job
from app.models.application import Application

from app.services.outreach_generator import (
    generate_outreach_message
)

from app.services.outreach_scheduler import (
    schedule_follow_up,
    get_scheduled_follow_ups
)

from app.services.application_outreach_service import (
    create_outreach_for_submitted_application
)


router = APIRouter(
    prefix="/outreach",
    tags=["Outreach"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# GENERATE OUTREACH FOR JOB
# ============================================================

@router.post("/generate/{job_id}")
def generate_outreach(
    job_id: int,
    candidate_name: str = "Candidate",
    db: Session = Depends(get_db)
):

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    result = generate_outreach_message(
        job=job,
        candidate_name=candidate_name
    )

    application = (
        db.query(Application)
        .filter(
            Application.job_id == job.id
        )
        .order_by(
            Application.id.desc()
        )
        .first()
    )

    outreach = Outreach(
        application_id=(
            application.id
            if application
            else None
        ),
        job_id=job.id,
        channel="EMAIL",
        subject=f"Interest in {job.title}",
        message=result["message"],
        status="DRAFT"
    )

    db.add(outreach)
    db.commit()
    db.refresh(outreach)

    return {
        "success": True,
        "outreach_id": outreach.id,
        "application_id": outreach.application_id,
        "job_id": job.id,
        "company": job.company,
        "job_title": job.title,
        "status": outreach.status,
        "message": outreach.message
    }


# ============================================================
# GENERATE OUTREACH FOR APPLICATION
# ============================================================

@router.post("/generate/application/{application_id}")
def generate_application_outreach(
    application_id: int,
    candidate_name: str = "Candidate",
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if not application:

        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    job = (
        db.query(Job)
        .filter(
            Job.id == application.job_id
        )
        .first()
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    result = generate_outreach_message(
        job=job,
        candidate_name=candidate_name
    )

    outreach = Outreach(
        application_id=application.id,
        job_id=job.id,
        channel="EMAIL",
        subject=f"Interest in {job.title}",
        message=result["message"],
        status="DRAFT"
    )

    db.add(outreach)
    db.commit()
    db.refresh(outreach)

    return {
        "success": True,
        "outreach_id": outreach.id,
        "application_id": application.id,
        "job_id": job.id,
        "company": job.company,
        "job_title": job.title,
        "status": outreach.status,
        "message": outreach.message
    }


# ============================================================
# GENERATE OUTREACH FOR SUBMITTED APPLICATION
# ============================================================

@router.post("/submitted-application/{application_id}")
def create_submitted_application_outreach(
    application_id: int,
    candidate_name: str = "Candidate",
    db: Session = Depends(get_db)
):

    result = create_outreach_for_submitted_application(
        db=db,
        application_id=application_id,
        candidate_name=candidate_name
    )

    if not result["success"]:

        raise HTTPException(
            status_code=400,
            detail=result
        )

    return result


# ============================================================
# GET ALL OUTREACH
# ============================================================

@router.get("/")
def get_outreach(
    db: Session = Depends(get_db)
):

    outreach_records = (
        db.query(Outreach)
        .order_by(
            Outreach.id.desc()
        )
        .all()
    )

    return {
        "success": True,
        "count": len(outreach_records),
        "outreach": [
            {
                column.name: getattr(
                    outreach,
                    column.name
                )
                for column in Outreach.__table__.columns
            }
            for outreach in outreach_records
        ]
    }


# ============================================================
# GET OUTREACH FOR APPLICATION
# ============================================================

@router.get("/application/{application_id}")
def get_application_outreach(
    application_id: int,
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if not application:

        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    outreach_records = (
        db.query(Outreach)
        .filter(
            Outreach.application_id
            == application_id
        )
        .order_by(
            Outreach.id.desc()
        )
        .all()
    )

    return {
        "success": True,
        "application_id": application_id,
        "count": len(outreach_records),
        "outreach": [
            {
                column.name: getattr(
                    outreach,
                    column.name
                )
                for column in Outreach.__table__.columns
            }
            for outreach in outreach_records
        ]
    }


# ============================================================
# SCHEDULE FOLLOW-UP
# ============================================================

@router.post("/{outreach_id}/schedule-follow-up")
def schedule_outreach_follow_up(
    outreach_id: int,
    days: int = 3,
    db: Session = Depends(get_db)
):

    result = schedule_follow_up(
        db=db,
        outreach_id=outreach_id,
        days=days
    )

    if not result["success"]:

        raise HTTPException(
            status_code=400,
            detail=result
        )

    return result


# ============================================================
# GET SCHEDULED FOLLOW-UPS
# ============================================================

@router.get("/follow-ups")
def get_follow_ups(
    db: Session = Depends(get_db)
):

    records = get_scheduled_follow_ups(
        db
    )

    return {
        "success": True,
        "count": len(records),
        "follow_ups": [
            {
                column.name: getattr(
                    record,
                    column.name
                )
                for column in Outreach.__table__.columns
            }
            for record in records
        ]
    }


# ============================================================
# GET SINGLE OUTREACH
# ============================================================

@router.get("/{outreach_id}")
def get_single_outreach(
    outreach_id: int,
    db: Session = Depends(get_db)
):

    outreach = (
        db.query(Outreach)
        .filter(
            Outreach.id == outreach_id
        )
        .first()
    )

    if not outreach:

        raise HTTPException(
            status_code=404,
            detail="Outreach record not found"
        )

    return {
        "success": True,
        "outreach": {
            column.name: getattr(
                outreach,
                column.name
            )
            for column in Outreach.__table__.columns
        }
    }


# ============================================================
# SCHEDULE OUTREACH
# ============================================================

@router.post("/{outreach_id}/schedule")
def schedule_outreach(
    outreach_id: int,
    scheduled_at: str,
    db: Session = Depends(get_db)
):

    outreach = (
        db.query(Outreach)
        .filter(
            Outreach.id == outreach_id
        )
        .first()
    )

    if not outreach:

        raise HTTPException(
            status_code=404,
            detail="Outreach record not found"
        )

    if outreach.status != "DRAFT":

        raise HTTPException(
            status_code=400,
            detail=(
                "Only DRAFT outreach "
                "can be scheduled"
            )
        )

    outreach.scheduled_at = scheduled_at
    outreach.status = "SCHEDULED"

    db.commit()
    db.refresh(outreach)

    return {
        "success": True,
        "outreach_id": outreach.id,
        "application_id": outreach.application_id,
        "status": outreach.status,
        "scheduled_at": outreach.scheduled_at
    }


# ============================================================
# MARK OUTREACH AS SENT
# ============================================================

@router.post("/{outreach_id}/mark-sent")
def mark_outreach_sent(
    outreach_id: int,
    db: Session = Depends(get_db)
):

    outreach = (
        db.query(Outreach)
        .filter(
            Outreach.id == outreach_id
        )
        .first()
    )

    if not outreach:

        raise HTTPException(
            status_code=404,
            detail="Outreach record not found"
        )

    if outreach.status not in [
        "SCHEDULED",
        "DRAFT"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only DRAFT or SCHEDULED "
                "outreach can be marked as sent"
            )
        )

    outreach.status = "SENT"

    outreach.sent_at = (
        datetime.now().isoformat()
    )

    db.commit()
    db.refresh(outreach)

    return {
        "success": True,
        "outreach_id": outreach.id,
        "application_id": outreach.application_id,
        "status": outreach.status,
        "sent_at": outreach.sent_at
    }


# ============================================================
# RECORD RECRUITER RESPONSE
# ============================================================

@router.post("/{outreach_id}/response")
def record_response(
    outreach_id: int,
    response_status: str,
    notes: str = "",
    db: Session = Depends(get_db)
):

    outreach = (
        db.query(Outreach)
        .filter(
            Outreach.id == outreach_id
        )
        .first()
    )

    if not outreach:

        raise HTTPException(
            status_code=404,
            detail="Outreach record not found"
        )

    outreach.response_status = response_status
    outreach.notes = notes
    outreach.status = "RESPONSE_RECEIVED"

    db.commit()
    db.refresh(outreach)

    return {
        "success": True,
        "outreach_id": outreach.id,
        "application_id": outreach.application_id,
        "status": outreach.status,
        "response_status": (
            outreach.response_status
        ),
        "notes": outreach.notes
    }