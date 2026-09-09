"""Core tracking logic: decide what is delivered and keep the store fresh."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

from .store import TrackedPackage, TrackingStore

# USPS event code "01" is the canonical "Delivered" event. We also match on
# text, since the summary/status wording is what most responses lead with.
_DELIVERED_EVENT_CODE = "01"
_DELIVERED_KEYWORDS = ("delivered", "left with individual", "picked up at")


def is_delivered(status: Dict[str, Any]) -> bool:
    """Return True if a normalized USPS status indicates delivery.

    Checks, in order: the top-level status/summary text, and then any
    tracking event whose code is the delivered code or whose description
    contains a delivery keyword.
    """
    text = f"{status.get('status', '')} {status.get('summary', '')}".lower()
    if any(keyword in text for keyword in _DELIVERED_KEYWORDS):
        return True
    for event in status.get("events", []):
        if str(event.get("code", "")).strip() == _DELIVERED_EVENT_CODE:
            return True
        desc = str(event.get("description", "")).lower()
        if any(keyword in desc for keyword in _DELIVERED_KEYWORDS):
            return True
    return False


@dataclass
class CheckResult:
    """The outcome of checking one package against USPS."""

    package: TrackedPackage
    status: Dict[str, Any]
    newly_delivered: bool
    error: str = ""


class Tracker:
    """Combines a USPS client with a local store of tracked packages."""

    def __init__(self, client: Any, store: TrackingStore) -> None:
        self.client = client
        self.store = store

    def check(self, package: TrackedPackage) -> CheckResult:
        """Query USPS for one package and update its stored status.

        ``newly_delivered`` is True only when this check is the one that
        flips the package from not-delivered to delivered, so callers can
        notify exactly once.
        """
        try:
            status = self.client.track(package.tracking_number)
        except Exception as exc:  # noqa: BLE001 - surface any client failure
            return CheckResult(package=package, status={}, newly_delivered=False, error=str(exc))

        delivered_now = is_delivered(status)
        newly_delivered = delivered_now and not package.delivered

        package.last_status = status.get("status", "")
        package.last_summary = status.get("summary", "")
        package.delivered = delivered_now
        package.last_checked = datetime.now(timezone.utc).isoformat(timespec="seconds")

        return CheckResult(
            package=package,
            status=status,
            newly_delivered=newly_delivered,
        )

    def check_all(self) -> List[CheckResult]:
        """Check every package in the store, persisting the results."""
        results = [self.check(pkg) for pkg in self.store.all()]
        self.store.save()
        return results
