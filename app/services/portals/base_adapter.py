from abc import ABC, abstractmethod


class BasePortalAdapter(ABC):
    """
    Base interface for all job portal adapters.
    """

    portal_name = "UNKNOWN"

    @abstractmethod
    def validate_application(self, application):
        """
        Validate whether an application can be
        submitted to the portal.
        """
        raise NotImplementedError

    @abstractmethod
    def submit_application(self, application):
        """
        Submit an application to the portal.

        Real browser/API submission will be implemented
        by the individual portal adapter.
        """
        raise NotImplementedError