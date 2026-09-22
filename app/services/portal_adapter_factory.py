from app.services.portals.adzuna_adapter import (
    AdzunaAdapter
)


def get_portal_adapter(portal_name):
    """
    Return the adapter for a supported portal.
    """

    if not portal_name:
        return None

    normalized_portal = (
        str(portal_name)
        .strip()
        .lower()
    )

    adapters = {
        "adzuna": AdzunaAdapter
    }

    adapter_class = adapters.get(
        normalized_portal
    )

    if not adapter_class:
        return None

    return adapter_class()


def get_supported_portals():
    """
    Return the portals that currently have
    adapters available.
    """

    return [
        "Adzuna"
    ]