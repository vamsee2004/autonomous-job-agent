from datetime import datetime

from sqlalchemy.orm import Session

from app.models.outreach import Outreach


def process_due_follow_ups(
    db: Session
):
    now = datetime.now()

    records = (
        db.query(Outreach)
        .filter(
            Outreach.status == "FOLLOW_UP_SCHEDULED"
        )
        .all()
    )

    processed = []

    for outreach in records:

        if not outreach.scheduled_at:
            continue

        try:
            scheduled_time = datetime.fromisoformat(
                outreach.scheduled_at
            )
        except ValueError:
            continue

        if scheduled_time <= now:

            outreach.status = "FOLLOW_UP_DUE"

            db.commit()
            db.refresh(outreach)

            processed.append(
                {
                    "outreach_id": outreach.id,
                    "application_id": (
                        outreach.application_id
                    ),
                    "job_id": outreach.job_id,
                    "status": outreach.status,
                    "scheduled_at": (
                        outreach.scheduled_at
                    )
                }
            )

    return {
        "success": True,
        "processed_count": len(processed),
        "follow_ups": processed
    }