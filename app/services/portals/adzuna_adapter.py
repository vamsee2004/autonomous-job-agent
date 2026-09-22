from app.services.portals.base_adapter import (
    BasePortalAdapter
)


class AdzunaAdapter(BasePortalAdapter):

    portal_name = "Adzuna"

    def validate_application(self, application):
        """
        Validate an Adzuna application before submission.
        """

        if not application:
            return {
                "allowed": False,
                "reason": "APPLICATION_NOT_FOUND"
            }

        if application.status != "APPROVED":
            return {
                "allowed": False,
                "reason": "APPLICATION_NOT_APPROVED"
            }

        if application.approved != 1:
            return {
                "allowed": False,
                "reason": "APPLICATION_APPROVAL_FLAG_NOT_SET"
            }

        return {
            "allowed": True,
            "reason": "VALIDATION_PASSED",
            "portal": self.portal_name
        }

    def submit_application(self, application):
        """
        Placeholder for actual Adzuna submission.

        External submission is intentionally not performed
        at this stage.
        """

        validation = (
            self.validate_application(
                application
            )
        )

        if not validation["allowed"]:
            return {
                "success": False,
                "reason": validation["reason"],
                "portal": self.portal_name
            }

        return {
            "success": False,
            "reason": "PORTAL_SUBMISSION_NOT_IMPLEMENTED",
            "message": (
                "Adzuna adapter is ready, but "
                "external portal submission is not "
                "implemented yet."
            ),
            "portal": self.portal_name,
            "application_id": application.id
        }