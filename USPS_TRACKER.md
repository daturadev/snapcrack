# USPS Delivery Tracker

A small command-line application that watches USPS tracking numbers headed
to your address and tells you the moment they are actually **delivered**.

- Track any number of packages with friendly labels.
- Check them on demand, or `watch` them on an interval until everything
  has arrived.
- Detects delivery from the USPS status text **and** the tracking events,
  and notifies you exactly once when a package flips to delivered.
- Pure Python standard library — **no dependencies to install**.
- A built-in `--demo` mode lets you try it without any USPS credentials.

## Setup

The tracker talks to the modern USPS APIs, which use OAuth2 client
credentials. Create a free developer account at
<https://developer.usps.com/>, make an app, and grab its **Consumer Key**
and **Consumer Secret**. Then expose them to the app:

```bash
export USPS_CONSUMER_KEY="your-consumer-key"
export USPS_CONSUMER_SECRET="your-consumer-secret"
```

No install step is required beyond Python 3.7+.

## Usage

```bash
# Start tracking a package (label is optional but nice)
python3 track_usps.py add 9400111899223197428490 --label "Running shoes"

# See everything you're tracking
python3 track_usps.py list

# Check all packages once against USPS
python3 track_usps.py check

# Poll every 10 minutes until all packages are delivered, then stop
python3 track_usps.py watch --interval 600

# Stop tracking a package
python3 track_usps.py remove 9400111899223197428490
```

### Try it without credentials

```bash
python3 track_usps.py add 9400111899DELIVERED-demo --label "Test box"
python3 track_usps.py --demo check
```

In `--demo` mode any tracking number containing the word `DELIVERED`
reports as delivered; everything else reports as in transit. You can also
set `USPS_DEMO=1` instead of passing the flag.

## How it decides something is "delivered"

`usps_tracker.tracker.is_delivered` checks, in order:

1. The top-level status/summary text (e.g. "Delivered").
2. Any tracking event with USPS event code `01` (the delivered code).
3. Any event whose description contains a delivery phrase
   ("delivered", "left with individual", "picked up at").

`watch` mode only announces a package once — the check that flips it from
not-delivered to delivered is the one that prints the notification.

## Where state is stored

Tracked packages and their last-seen status live in a JSON file at
`~/.usps_tracker.json` (override with `--store /path/to/file.json`). This
is what lets `watch` remember what it has already reported.

## Project layout

```
track_usps.py            # CLI entry point
usps_tracker/
  __init__.py            # package exports
  client.py              # USPS OAuth2 API client + offline DemoClient
  store.py               # JSON persistence of tracked packages
  tracker.py             # delivered-detection + check orchestration
  cli.py                 # argparse command-line interface
tests/
  test_usps_tracker.py   # unit tests (python3 -m unittest discover -s tests)
```

## Running the tests

```bash
python3 -m unittest discover -s tests
```
