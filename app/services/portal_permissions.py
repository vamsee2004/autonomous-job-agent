import json
from pathlib import Path

from app.services.logger import logger


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


PERMISSIONS_PATH = (
    PROJECT_ROOT
    / "app"
    / "knowledge"
    / "portal_permissions.json"
)


DEFAULT_PERMISSIONS = {
    "Adzuna": {
        "enabled": True,
        "mode": "APPROVAL_REQUIRED"
    },

    "Naukri": {
        "enabled": False,
        "mode": "APPROVAL_REQUIRED"
    },

    "LinkedIn": {
        "enabled": False,
        "mode": "APPROVAL_REQUIRED"
    },

    "Indeed": {
        "enabled": False,
        "mode": "APPROVAL_REQUIRED"
    },

    "Glassdoor": {
        "enabled": False,
        "mode": "APPROVAL_REQUIRED"
    }
}


ALLOWED_MODES = [
    "FULLY_AUTONOMOUS",
    "APPROVAL_REQUIRED",
    "ASSISTED"
]


def ensure_permissions_file():

    PERMISSIONS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not PERMISSIONS_PATH.exists():

        with open(
            PERMISSIONS_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                DEFAULT_PERMISSIONS,
                file,
                indent=4
            )


def load_portal_permissions():

    ensure_permissions_file()

    try:

        with open(
            PERMISSIONS_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except json.JSONDecodeError:

        logger.error(
            "Portal permissions file contains "
            "invalid JSON"
        )

        return DEFAULT_PERMISSIONS.copy()


def save_portal_permissions(
    permissions
):

    ensure_permissions_file()

    with open(
        PERMISSIONS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            permissions,
            file,
            indent=4
        )


def get_portal_permission(
    portal: str
):

    permissions = (
        load_portal_permissions()
    )

    permission = permissions.get(
        portal
    )

    if permission is None:

        return {
            "portal": portal,
            "enabled": False,
            "mode": "APPROVAL_REQUIRED",
            "configured": False
        }

    return {
        "portal": portal,
        "enabled": permission.get(
            "enabled",
            False
        ),
        "mode": permission.get(
            "mode",
            "APPROVAL_REQUIRED"
        ),
        "configured": True
    }


def check_portal_permission(
    portal: str
):

    permission = (
        get_portal_permission(
            portal
        )
    )

    if not permission["configured"]:

        return {
            "allowed": False,
            "reason": "PORTAL_NOT_CONFIGURED",
            "portal": portal,
            "permission": permission
        }

    if not permission["enabled"]:

        return {
            "allowed": False,
            "reason": "PORTAL_DISABLED",
            "portal": portal,
            "permission": permission
        }

    return {
        "allowed": True,
        "reason": "PORTAL_ENABLED",
        "portal": portal,
        "mode": permission["mode"],
        "permission": permission
    }


def update_portal_permission(
    portal: str,
    enabled: bool,
    mode: str
):

    if mode not in ALLOWED_MODES:

        return {
            "success": False,
            "message": (
                "Invalid portal automation mode"
            ),
            "allowed_modes": ALLOWED_MODES
        }

    permissions = (
        load_portal_permissions()
    )

    permissions[portal] = {
        "enabled": enabled,
        "mode": mode
    }

    save_portal_permissions(
        permissions
    )

    logger.info(
        f"Portal permission updated: "
        f"portal={portal}, "
        f"enabled={enabled}, "
        f"mode={mode}"
    )

    return {
        "success": True,
        "portal": portal,
        "enabled": enabled,
        "mode": mode
    }


def get_all_portal_permissions():

    permissions = (
        load_portal_permissions()
    )

    return {
        "success": True,
        "portals": permissions
    }