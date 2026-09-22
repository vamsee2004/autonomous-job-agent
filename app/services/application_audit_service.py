from datetime import datetime

from sqlalchemy.orm import Session

from app.models.application_audit import (
    ApplicationAudit
)


def create_application_audit(
    db: Session,
    application_id: int,
    job_id: int = None,
    action: str = "STATUS_CHANGE",
    old_status: str = None,
    new_status: str = None,
    details: str = None
):
    audit = ApplicationAudit(
        application_id=application_id,
        job_id=job_id,
        action=action,
        old_status=old_status,
        new_status=new_status,
        details=details,
        created_at=datetime.now().isoformat()
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit


def get_application_audit_history(
    db: Session,
    application_id: int
):
    return (
        db.query(ApplicationAudit)
        .filter(
            ApplicationAudit.application_id
            == application_id
        )
        .order_by(
            ApplicationAudit.id.asc()
        )
        .all()
    )