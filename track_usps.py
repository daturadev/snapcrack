#!/usr/bin/env python3
"""Entry point for the USPS delivery tracker.

Run ``python3 track_usps.py --help`` for usage. See usps_tracker/ for the
implementation.
"""

from usps_tracker.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
