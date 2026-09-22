from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.outreach import Outreach


DEFAULT_FOLLOW_UP_DAYS = 3


def schedule_follow_up(
    db: Session,
    outreach_id: int,
    days: int = DEFAULT_FOLLOW_UP_DAYS
):
    """
    Schedule a follow-up for an outreach record.
    """

    outreach = (
        db.query(Outreach)
        .filter(
            Outreach.id == outreach_id
        )
        .first()
    )

    if not outreach:
        return {
            "success": False,
            "reason": "OUTREACH_NOT_FOUND"
        }

    if outreach.status != "SENT":
        return {
            "success": False,
            "reason": "OUTREACH_NOT_SENT",
            "message": (
                "Follow-up can only be scheduled "
                "after outreach has been sent."
            )
        }

    if days < 1:
        return {
            "success": False,
            "reason": "INVALID_FOLLOW_UP_DAYS"
        }

    follow_up_time = (
        datetime.now()
        + timedelta(days=days)
    )

    outreach.scheduled_at = (
        follow_up_time.isoformat()
    )

    outreach.status = "FOLLOW_UP_SCHEDULED"

    db.commit()
    db.refresh(outreach)

    return {
        "success": True,
        "outreach_id": outreach.id,
        "application_id": outreach.application_id,
        "status": outreach.status,
        "follow_up_at": outreach.scheduled_at,
        "days": days
    }


def get_scheduled_follow_ups(
    db: Session
):
    """
    Return outreach records that have
    follow-ups scheduled.
    """

    records = (
        db.query(Outreach)
        .filter(
            Outreach.status
            == "FOLLOW_UP_SCHEDULED"
        )
        .order_by(
            Outreach.scheduled_at.asc()
        )
        .all()
    )

    return records