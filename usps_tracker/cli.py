"""Command-line interface for the USPS delivery tracker.

Commands:
    add <tracking_number> [--label NAME]   register a package to watch
    remove <tracking_number>               stop watching a package
    list                                   show all watched packages
    check                                  check every package once
    watch [--interval SECONDS]             poll until everything is delivered

Credentials come from the environment:
    USPS_CONSUMER_KEY, USPS_CONSUMER_SECRET   (real USPS API)

Pass --demo (or set USPS_DEMO=1) to use a built-in offline fake client so
you can try the app without any credentials.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any, List

from .client import DemoClient, USPSClient, USPSError
from .store import DEFAULT_STORE_PATH, TrackingStore
from .tracker import CheckResult, Tracker


def build_client(args: argparse.Namespace) -> Any:
    """Return a real or demo USPS client based on flags/environment."""
    if args.demo or os.environ.get("USPS_DEMO") == "1":
        return DemoClient()
    key = os.environ.get("USPS_CONSUMER_KEY", "")
    secret = os.environ.get("USPS_CONSUMER_SECRET", "")
    return USPSClient(key, secret)


def _print_result(result: CheckResult) -> None:
    """Print a single check result in a readable one-or-two-line form."""
    pkg = result.package
    name = pkg.display_name()
    if result.error:
        print(f"  [!] {name}: could not check ({result.error})")
        return
    icon = "[DELIVERED]" if pkg.delivered else "[  in transit  ]"
    status = pkg.last_summary or pkg.last_status or "Unknown"
    print(f"  {icon} {name}: {status}")
    exp = result.status.get("expected_delivery")
    if exp and not pkg.delivered:
        print(f"                expected delivery: {exp}")
    if result.newly_delivered:
        print(f"  *** {name} was just DELIVERED to your address! ***")


def cmd_add(args: argparse.Namespace) -> int:
    store = TrackingStore.load(args.store)
    pkg = store.add(args.tracking_number, label=args.label or "")
    store.save()
    print(f"Now tracking {pkg.display_name()} ({pkg.tracking_number}).")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    store = TrackingStore.load(args.store)
    if store.remove(args.tracking_number):
        store.save()
        print(f"Stopped tracking {args.tracking_number}.")
        return 0
    print(f"{args.tracking_number} was not being tracked.")
    return 1


def cmd_list(args: argparse.Namespace) -> int:
    store = TrackingStore.load(args.store)
    packages = store.all()
    if not packages:
        print("No packages are being tracked yet. Add one with:")
        print("  track_usps.py add <tracking_number> --label \"My package\"")
        return 0
    print(f"Tracking {len(packages)} package(s):")
    for pkg in packages:
        state = "delivered" if pkg.delivered else "in transit / unknown"
        checked = f" (checked {pkg.last_checked})" if pkg.last_checked else ""
        print(f"  - {pkg.display_name()} [{pkg.tracking_number}] -> {state}{checked}")
    return 0


def _run_check(args: argparse.Namespace) -> List[CheckResult]:
    store = TrackingStore.load(args.store)
    if not store.all():
        print("No packages are being tracked yet. Add one with 'add' first.")
        return []
    client = build_client(args)
    tracker = Tracker(client, store)
    return tracker.check_all()


def cmd_check(args: argparse.Namespace) -> int:
    results = _run_check(args)
    if not results:
        return 0
    print("Checking your packages with USPS...")
    for result in results:
        _print_result(result)
    delivered = sum(1 for r in results if r.package.delivered)
    print(f"\n{delivered}/{len(results)} delivered.")
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    interval = max(args.interval, 30)
    print(
        f"Watching your packages (every {interval}s). "
        "Press Ctrl-C to stop.\n"
    )
    try:
        while True:
            store = TrackingStore.load(args.store)
            pending = [p for p in store.all() if not p.delivered]
            if not store.all():
                print("No packages are being tracked. Add one with 'add' first.")
                return 0
            if not pending:
                print("All tracked packages have been delivered. Done!")
                return 0

            client = build_client(args)
            tracker = Tracker(client, store)
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{stamp}] Checking {len(pending)} pending package(s)...")
            for pkg in pending:
                result = tracker.check(pkg)
                _print_result(result)
            store.save()

            if all(p.delivered for p in store.all()):
                print("\nEverything has been delivered to your address. Done!")
                return 0
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped watching.")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="track_usps.py",
        description="Track USPS packages and know when they reach your address.",
    )
    parser.add_argument(
        "--store",
        default=DEFAULT_STORE_PATH,
        help=f"path to the tracking store file (default: {DEFAULT_STORE_PATH})",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="use the offline demo client (no USPS credentials needed)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="start tracking a package")
    p_add.add_argument("tracking_number")
    p_add.add_argument("--label", help="a friendly name for this package")
    p_add.set_defaults(func=cmd_add)

    p_rm = sub.add_parser("remove", help="stop tracking a package")
    p_rm.add_argument("tracking_number")
    p_rm.set_defaults(func=cmd_remove)

    p_list = sub.add_parser("list", help="list tracked packages")
    p_list.set_defaults(func=cmd_list)

    p_check = sub.add_parser("check", help="check all packages once")
    p_check.set_defaults(func=cmd_check)

    p_watch = sub.add_parser(
        "watch", help="poll repeatedly until all packages are delivered"
    )
    p_watch.add_argument(
        "--interval",
        type=int,
        default=600,
        help="seconds between checks (minimum 30, default 600)",
    )
    p_watch.set_defaults(func=cmd_watch)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except USPSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(
            "Tip: run with --demo to try the app without USPS credentials.",
            file=sys.stderr,
        )
        return 2
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
