# ============================================================
# APPLICATION STATE MACHINE
# ============================================================

ALLOWED_STATUSES = {
    "PENDING_APPROVAL",
    "READY",
    "APPROVED",
    "SUBMITTED",
    "REJECTED",
    "WITHDRAWN"
}


ALLOWED_TRANSITIONS = {

    "PENDING_APPROVAL": {
        "READY",
        "APPROVED",
        "REJECTED",
        "WITHDRAWN"
    },

    "READY": {
        "APPROVED",
        "REJECTED",
        "WITHDRAWN"
    },

    "APPROVED": {
        "SUBMITTED",
        "REJECTED",
        "WITHDRAWN"
    },

    "SUBMITTED": {
        "REJECTED",
        "WITHDRAWN"
    },

    "REJECTED": set(),

    "WITHDRAWN": set()
}


def normalize_status(
    status: str
):
    """
    Normalize an application status.
    """

    if status is None:
        return ""

    return (
        str(status)
        .strip()
        .upper()
    )


def is_valid_status(
    status: str
):
    """
    Check whether a status is supported.
    """

    normalized_status = (
        normalize_status(status)
    )

    return (
        normalized_status
        in ALLOWED_STATUSES
    )


def can_transition(
    current_status: str,
    new_status: str
):
    """
    Check whether an application can move
    from its current status to the new status.
    """

    current = normalize_status(
        current_status
    )

    new = normalize_status(
        new_status
    )

    if not is_valid_status(current):

        return {
            "allowed": False,
            "reason": "INVALID_CURRENT_STATUS",
            "current_status": current,
            "new_status": new
        }

    if not is_valid_status(new):

        return {
            "allowed": False,
            "reason": "INVALID_NEW_STATUS",
            "current_status": current,
            "new_status": new
        }

    if current == new:

        return {
            "allowed": False,
            "reason": "STATUS_ALREADY_SET",
            "current_status": current,
            "new_status": new
        }

    allowed_next_states = (
        ALLOWED_TRANSITIONS.get(
            current,
            set()
        )
    )

    if new not in allowed_next_states:

        return {
            "allowed": False,
            "reason": "INVALID_STATUS_TRANSITION",
            "current_status": current,
            "new_status": new,
            "allowed_next_statuses": sorted(
                allowed_next_states
            )
        }

    return {
        "allowed": True,
        "reason": "VALID_STATUS_TRANSITION",
        "current_status": current,
        "new_status": new
    }


def get_allowed_next_statuses(
    current_status: str
):
    """
    Return all valid next states for an application.
    """

    current = normalize_status(
        current_status
    )

    if not is_valid_status(current):

        return []

    return sorted(
        ALLOWED_TRANSITIONS.get(
            current,
            set()
        )
    )