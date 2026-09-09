"""USPS tracking API client.

Uses the modern USPS APIs (https://apis.usps.com) which authenticate with
OAuth2 client credentials. You need a free developer account at
https://developer.usps.com/ to obtain a Consumer Key and Consumer Secret,
then expose them to this app as environment variables:

    export USPS_CONSUMER_KEY="..."
    export USPS_CONSUMER_SECRET="..."

The client fetches a bearer token and calls the Tracking v3 endpoint. The
raw JSON returned by USPS is normalized into a small, stable dict so the
rest of the app does not depend on USPS response quirks.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

# Production USPS API host. The test/CAT environment is apis-tem.usps.com;
# override with USPS_API_BASE if you want to point at it.
DEFAULT_API_BASE = "https://apis.usps.com"

# HTTP timeout (seconds) for every request to USPS.
HTTP_TIMEOUT = 30


class USPSError(RuntimeError):
    """Raised when the USPS API cannot be reached or returns an error."""


class USPSClient:
    """Thin client over the USPS OAuth2 tracking API.

    The only method the rest of the app relies on is :meth:`track`, which
    returns a normalized status dict (see :meth:`_normalize`).
    """

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        api_base: str = DEFAULT_API_BASE,
    ) -> None:
        if not consumer_key or not consumer_secret:
            raise USPSError(
                "USPS credentials missing. Set USPS_CONSUMER_KEY and "
                "USPS_CONSUMER_SECRET (get them at https://developer.usps.com/)."
            )
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.api_base = api_base.rstrip("/")
        self._token: Optional[str] = None
        self._token_expiry: float = 0.0

    # -- authentication -------------------------------------------------

    def _get_token(self) -> str:
        """Return a cached OAuth2 bearer token, refreshing when needed."""
        if self._token and time.time() < self._token_expiry - 60:
            return self._token

        url = f"{self.api_base}/oauth2/v3/token"
        payload = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self.consumer_key,
                "client_secret": self.consumer_secret,
            }
        ).encode()
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        data = self._send(req, context="requesting OAuth token")
        token = data.get("access_token")
        if not token:
            raise USPSError(f"USPS token response had no access_token: {data}")
        self._token = token
        self._token_expiry = time.time() + float(data.get("expires_in", 3600))
        return token

    # -- public API -----------------------------------------------------

    def track(self, tracking_number: str) -> Dict[str, Any]:
        """Look up one tracking number and return a normalized status dict."""
        token = self._get_token()
        number = urllib.parse.quote(tracking_number.strip())
        url = f"{self.api_base}/tracking/v3/tracking/{number}?expand=DETAIL"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            method="GET",
        )
        raw = self._send(req, context=f"tracking {tracking_number}")
        return self._normalize(tracking_number, raw)

    # -- helpers --------------------------------------------------------

    @staticmethod
    def _normalize(tracking_number: str, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce a USPS tracking response to a stable, minimal shape."""
        summary = raw.get("trackingSummary") or raw.get("statusSummary") or ""
        status = raw.get("status") or raw.get("statusCategory") or ""
        events = raw.get("trackingEvents") or raw.get("eventSummaries") or []

        normalized_events = []
        for ev in events:
            if isinstance(ev, str):
                normalized_events.append({"description": ev})
                continue
            normalized_events.append(
                {
                    "type": ev.get("eventType") or ev.get("event") or "",
                    "code": ev.get("eventCode") or "",
                    "timestamp": ev.get("eventTimestamp") or ev.get("date") or "",
                    "city": ev.get("eventCity") or "",
                    "state": ev.get("eventState") or "",
                    "zip": ev.get("eventZIP") or ev.get("eventZip") or "",
                    "description": ev.get("eventType")
                    or ev.get("event")
                    or ev.get("description")
                    or "",
                }
            )

        return {
            "tracking_number": tracking_number,
            "status": status,
            "summary": summary,
            "expected_delivery": raw.get("expectedDeliveryDate")
            or raw.get("predictedDeliveryDate")
            or "",
            "events": normalized_events,
        }

    @staticmethod
    def _send(req: urllib.request.Request, *, context: str) -> Dict[str, Any]:
        """Perform an HTTP request and decode the JSON body, or raise."""
        try:
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8")
            except Exception:  # noqa: BLE001 - best-effort detail extraction
                pass
            raise USPSError(
                f"USPS API error while {context}: HTTP {exc.code} {detail}".strip()
            ) from exc
        except urllib.error.URLError as exc:
            raise USPSError(f"Could not reach USPS while {context}: {exc.reason}") from exc

        try:
            return json.loads(body) if body else {}
        except json.JSONDecodeError as exc:
            raise USPSError(f"USPS returned invalid JSON while {context}: {body[:200]}") from exc


class DemoClient:
    """Offline fake client so the app can be tried without credentials.

    It returns deterministic, canned statuses. Any tracking number that
    contains the substring ``DELIVERED`` (case-insensitive) reports as
    delivered; everything else reports as in transit. This makes the demo
    predictable and lets the test suite exercise the real code paths
    without hitting the network.
    """

    def track(self, tracking_number: str) -> Dict[str, Any]:
        delivered = "delivered" in tracking_number.lower()
        if delivered:
            return {
                "tracking_number": tracking_number,
                "status": "Delivered",
                "summary": "Your item was delivered in or at the mailbox.",
                "expected_delivery": "",
                "events": [
                    {
                        "type": "Delivered",
                        "code": "01",
                        "timestamp": "2026-09-09T13:12:00Z",
                        "city": "SPRINGFIELD",
                        "state": "IL",
                        "zip": "62704",
                        "description": "Delivered, In/At Mailbox",
                    }
                ],
            }
        return {
            "tracking_number": tracking_number,
            "status": "In Transit",
            "summary": "In Transit to Next Facility",
            "expected_delivery": "2026-09-11",
            "events": [
                {
                    "type": "In Transit",
                    "code": "NT",
                    "timestamp": "2026-09-08T04:30:00Z",
                    "city": "ST LOUIS",
                    "state": "MO",
                    "zip": "63101",
                    "description": "In Transit to Next Facility",
                }
            ],
        }
