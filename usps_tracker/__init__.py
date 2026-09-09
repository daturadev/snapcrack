"""USPS delivery tracker.

A small application that watches USPS tracking numbers headed to your
address and tells you when they have actually been delivered.

Public API:
    USPSClient        -- talks to the USPS OAuth2 tracking API
    DemoClient        -- offline fake client for testing / trying it out
    TrackingStore     -- local JSON persistence of tracked packages
    Tracker           -- ties the client and store together
    TrackedPackage    -- a single package + its latest known status
    is_delivered      -- helper that decides if a status means "delivered"
"""

from .client import USPSClient, DemoClient, USPSError
from .store import TrackingStore, TrackedPackage
from .tracker import Tracker, is_delivered

__all__ = [
    "USPSClient",
    "DemoClient",
    "USPSError",
    "TrackingStore",
    "TrackedPackage",
    "Tracker",
    "is_delivered",
]

__version__ = "1.0.0"
