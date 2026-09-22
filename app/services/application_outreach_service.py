from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.job import Job
from app.models.outreach import Outreach

from app.services.outreach_generator import (
    generate_outreach_message
)


def create_outreach_for_submitted_application(
    db: Session,
    application_id: int,
    candidate_name: str = "Candidate"
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if not application:
        return {
            "success": False,
            "reason": "APPLICATION_NOT_FOUND"
        }

    if application.status != "SUBMITTED":
        return {
            "success": False,
            "reason": "APPLICATION_NOT_SUBMITTED",
            "message": (
                "Outreach can only be created "
                "for submitted applications."
            )
        }

    job = (
        db.query(Job)
        .filter(
            Job.id == application.job_id
        )
        .first()
    )

    if not job:
        return {
            "success": False,
            "reason": "JOB_NOT_FOUND"
        }

    existing_outreach = (
        db.query(Outreach)
        .filter(
            Outreach.application_id
            == application.id
        )
        .first()
    )

    if existing_outreach:
        return {
            "success": False,
            "reason": "OUTREACH_ALREADY_EXISTS",
            "outreach_id": existing_outreach.id
        }

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