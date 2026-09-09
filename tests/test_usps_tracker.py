"""Tests for the USPS delivery tracker.

Run with:  python3 -m unittest discover -s tests
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from usps_tracker.client import DemoClient  # noqa: E402
from usps_tracker.store import TrackingStore  # noqa: E402
from usps_tracker.tracker import Tracker, is_delivered  # noqa: E402


class IsDeliveredTests(unittest.TestCase):
    def test_delivered_by_status_text(self):
        self.assertTrue(is_delivered({"status": "Delivered", "summary": "", "events": []}))

    def test_delivered_by_summary_text(self):
        status = {"status": "", "summary": "Your item was delivered", "events": []}
        self.assertTrue(is_delivered(status))

    def test_delivered_by_event_code(self):
        status = {"status": "", "summary": "", "events": [{"code": "01", "description": ""}]}
        self.assertTrue(is_delivered(status))

    def test_not_delivered_in_transit(self):
        status = {
            "status": "In Transit",
            "summary": "In Transit to Next Facility",
            "events": [{"code": "NT", "description": "In Transit"}],
        }
        self.assertFalse(is_delivered(status))


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        for p in (self.path, f"{self.path}.tmp"):
            if os.path.exists(p):
                os.remove(p)

    def test_add_persists_across_reload(self):
        store = TrackingStore.load(self.path)
        store.add("9400111899223197428490", label="Shoes")
        store.save()

        reloaded = TrackingStore.load(self.path)
        pkg = reloaded.get("9400111899223197428490")
        self.assertIsNotNone(pkg)
        self.assertEqual(pkg.label, "Shoes")
        self.assertEqual(pkg.display_name(), "Shoes")

    def test_add_is_idempotent_and_updates_label(self):
        store = TrackingStore.load(self.path)
        store.add("ABC")
        store.add("ABC", label="Renamed")
        self.assertEqual(len(store.all()), 1)
        self.assertEqual(store.get("ABC").label, "Renamed")

    def test_remove(self):
        store = TrackingStore.load(self.path)
        store.add("XYZ")
        self.assertTrue(store.remove("XYZ"))
        self.assertFalse(store.remove("XYZ"))

    def test_empty_tracking_number_rejected(self):
        store = TrackingStore.load(self.path)
        with self.assertRaises(ValueError):
            store.add("   ")

    def test_corrupt_file_starts_fresh(self):
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write("this is not json{{{")
        store = TrackingStore.load(self.path)
        self.assertEqual(store.all(), [])


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        for p in (self.path, f"{self.path}.tmp"):
            if os.path.exists(p):
                os.remove(p)

    def test_newly_delivered_flips_only_once(self):
        store = TrackingStore.load(self.path)
        pkg = store.add("PKG-DELIVERED-1")
        tracker = Tracker(DemoClient(), store)

        first = tracker.check(pkg)
        self.assertTrue(first.newly_delivered)
        self.assertTrue(pkg.delivered)

        second = tracker.check(pkg)
        self.assertFalse(second.newly_delivered)
        self.assertTrue(pkg.delivered)

    def test_in_transit_not_delivered(self):
        store = TrackingStore.load(self.path)
        pkg = store.add("PKG-IN-TRANSIT")
        tracker = Tracker(DemoClient(), store)
        result = tracker.check(pkg)
        self.assertFalse(result.newly_delivered)
        self.assertFalse(pkg.delivered)

    def test_check_all_persists(self):
        store = TrackingStore.load(self.path)
        store.add("PKG-DELIVERED-A")
        store.add("PKG-STILL-GOING")
        tracker = Tracker(DemoClient(), store)
        results = tracker.check_all()
        self.assertEqual(len(results), 2)

        reloaded = TrackingStore.load(self.path)
        self.assertTrue(reloaded.get("PKG-DELIVERED-A").delivered)
        self.assertFalse(reloaded.get("PKG-STILL-GOING").delivered)

    def test_client_error_is_captured(self):
        class BoomClient:
            def track(self, tracking_number):
                raise RuntimeError("network down")

        store = TrackingStore.load(self.path)
        pkg = store.add("PKG")
        tracker = Tracker(BoomClient(), store)
        result = tracker.check(pkg)
        self.assertEqual(result.error, "network down")
        self.assertFalse(pkg.delivered)


if __name__ == "__main__":
    unittest.main()
