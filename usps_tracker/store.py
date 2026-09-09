"""Local persistence for the packages you are tracking.

Packages are stored in a small JSON file (``~/.usps_tracker.json`` by
default). Each entry records the tracking number, an optional human label,
and the last status we saw so ``watch`` mode can detect changes and avoid
spamming notifications.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

DEFAULT_STORE_PATH = os.path.expanduser("~/.usps_tracker.json")


@dataclass
class TrackedPackage:
    """A package being watched, plus the last status we observed for it."""

    tracking_number: str
    label: str = ""
    last_status: str = ""
    last_summary: str = ""
    delivered: bool = False
    last_checked: str = ""

    def display_name(self) -> str:
        """A friendly name for output: the label if set, else the number."""
        return self.label or self.tracking_number


@dataclass
class TrackingStore:
    """Loads and saves a set of :class:`TrackedPackage` records."""

    path: str = DEFAULT_STORE_PATH
    packages: Dict[str, TrackedPackage] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str = DEFAULT_STORE_PATH) -> "TrackingStore":
        """Read the store from disk, returning an empty store if absent."""
        store = cls(path=path)
        if not os.path.exists(path):
            return store
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError):
            # A corrupt or unreadable store should not crash the app; start
            # fresh rather than lose the ability to track anything.
            return store
        for item in data.get("packages", []):
            pkg = TrackedPackage(
                tracking_number=item.get("tracking_number", ""),
                label=item.get("label", ""),
                last_status=item.get("last_status", ""),
                last_summary=item.get("last_summary", ""),
                delivered=bool(item.get("delivered", False)),
                last_checked=item.get("last_checked", ""),
            )
            if pkg.tracking_number:
                store.packages[pkg.tracking_number] = pkg
        return store

    def save(self) -> None:
        """Persist the store to disk atomically."""
        data = {"packages": [asdict(p) for p in self.packages.values()]}
        tmp = f"{self.path}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp, self.path)

    def add(self, tracking_number: str, label: str = "") -> TrackedPackage:
        """Add a package (or update its label if already present)."""
        tracking_number = tracking_number.strip()
        if not tracking_number:
            raise ValueError("Tracking number cannot be empty.")
        existing = self.packages.get(tracking_number)
        if existing:
            if label:
                existing.label = label
            return existing
        pkg = TrackedPackage(tracking_number=tracking_number, label=label)
        self.packages[tracking_number] = pkg
        return pkg

    def remove(self, tracking_number: str) -> bool:
        """Remove a package. Returns True if something was removed."""
        return self.packages.pop(tracking_number.strip(), None) is not None

    def get(self, tracking_number: str) -> Optional[TrackedPackage]:
        return self.packages.get(tracking_number.strip())

    def all(self) -> List[TrackedPackage]:
        return list(self.packages.values())
