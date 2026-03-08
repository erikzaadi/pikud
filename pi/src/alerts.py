#!/usr/bin/env python3
"""
Red Alert monitor - polls Pikud HaOref API and prints status changes
for a configured city.
"""

import time
import json
import logging
from enum import Enum
from datetime import datetime

import os

import requests
from dotenv import load_dotenv

import particle_notifier
from gpio_led import AlertLED

load_dotenv()

# --- Constants ---
ALERTS_URL = "https://www.oref.org.il/WarningMessages/alert/alerts.json"
ALERTS_HISTORY_URL = (
    "https://www.oref.org.il"
    "/warningMessages/alert/History/AlertsHistory.json"
)
HISTORY_WINDOW = 1800  # seconds - ignore history entries older than this

CITY = os.getenv("CITY", "תל אביב")  # must match oref API exactly

POLL_INTERVAL = 10       # seconds between normal polls
BACKOFF_BASE = 10        # initial backoff on error (seconds)
BACKOFF_MAX = 300        # max backoff (5 minutes)
# seconds to stay in RESOLVED before returning to NO_ALERTS
RESOLVED_DURATION = 300

REQUEST_HEADERS = {
    "Referer": "https://www.oref.org.il/",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


# --- Alert status ---
class AlertStatus(Enum):
    NO_ALERTS = "no_alerts"
    PRE_WARNING = "pre_warning"   # cat 14 - alerts expected in area soon
    ALERT = "alert"
    RESOLVED = "resolved"


ACTIVE_STATUSES = (
    AlertStatus.PRE_WARNING,
    AlertStatus.ALERT,
)

CAT_PRE_WARNING = 14
CAT_EVENT_ENDED = 13



def fetch_alerts(session: requests.Session) -> dict | None:
    """
    Fetch current active alerts from the API.
    Returns parsed JSON dict, or None if there are no active alerts.
    """
    resp = session.get(ALERTS_URL, headers=REQUEST_HEADERS, timeout=10)
    resp.raise_for_status()
    # API returns UTF-8 with BOM when active, empty body when quiet
    text = resp.content.decode("utf-8-sig").strip()
    if not text:
        return None
    return json.loads(text)


def _parse_history_entries(resp: requests.Response) -> list:
    """Decode and parse history JSON, repairing truncation if needed."""
    text = resp.content.decode("utf-8-sig", errors="ignore")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        last_brace = text.rfind("}")
        if last_brace == -1:
            return []
        return json.loads(text[: last_brace + 1] + "]")


def _status_from_category(cat: int | None) -> AlertStatus:
    if cat == CAT_PRE_WARNING:
        return AlertStatus.PRE_WARNING
    return AlertStatus.ALERT


def fetch_history_status(
    session: requests.Session, city: str
) -> tuple:
    """
    Check recent alert history for the city.
    Returns (AlertStatus, alert_info_dict | None).

    If the most recent history entry for the city is not cat 13
    and is within HISTORY_WINDOW seconds, the alert is still active.
    """
    try:
        resp = session.get(
            ALERTS_HISTORY_URL, headers=REQUEST_HEADERS, timeout=15
        )
        resp.raise_for_status()
        entries = _parse_history_entries(resp)
    except Exception as e:
        logging.warning(f"History fetch failed: {e}")
        return AlertStatus.NO_ALERTS, None

    now = datetime.now()
    city_entries = [
        e for e in entries if e.get("data", "").strip() == city
    ]
    if not city_entries:
        return AlertStatus.NO_ALERTS, None

    # Entries are newest-first; take the most recent one
    latest = city_entries[0]
    try:
        entry_time = datetime.strptime(
            latest["alertDate"], "%Y-%m-%d %H:%M:%S"
        )
        age = (now - entry_time).total_seconds()
    except Exception:
        return AlertStatus.NO_ALERTS, None

    if age > HISTORY_WINDOW:
        return AlertStatus.NO_ALERTS, None

    cat = latest.get("category")
    if cat == CAT_EVENT_ENDED:
        return AlertStatus.NO_ALERTS, None

    status = _status_from_category(cat)
    return status, {"title": latest.get("title", ""), "cat": cat}


def resolve_status(
    alert_data: dict | None, city: str
) -> tuple:
    """
    Determine alert status for the monitored city.
    Returns (AlertStatus, alert_info_dict | None).
    """
    if not alert_data or not alert_data.get("data"):
        return AlertStatus.NO_ALERTS, None

    cities_in_alert = [c.strip() for c in alert_data["data"]]
    if city not in cities_in_alert:
        return AlertStatus.NO_ALERTS, None

    raw_cat = alert_data.get("cat")
    try:
        cat: int | None = int(raw_cat) if raw_cat is not None else None
    except (TypeError, ValueError):
        cat = None

    if cat == CAT_EVENT_ENDED:
        return AlertStatus.NO_ALERTS, None

    status = _status_from_category(cat)
    return status, {
        "id": alert_data.get("id"),
        "title": alert_data.get("title", ""),
        "cat": cat,
    }


def format_message(
    status: AlertStatus,
    city: str,
    info: dict | None,
    resolved_until: float | None = None,
) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if status == AlertStatus.NO_ALERTS:
        return f"[{ts}] No active alerts for {city}"

    if status == AlertStatus.RESOLVED:
        remaining = (
            max(0, int(resolved_until - time.monotonic()))
            if resolved_until else 0
        )
        return (
            f"[{ts}] RESOLVED - alert cleared for {city}"
            f" (all-clear in {remaining}s)"
        )

    title = info.get("title", "") if info else ""

    if status == AlertStatus.PRE_WARNING:
        return f"[{ts}] ALERT SOON: {title} | City: {city}"

    return f"[{ts}] ALERT: {title} | City: {city} | GO TO SHELTER NOW"


def _compute_new_status(
    current_status: AlertStatus,
    live_status: AlertStatus,
    resolved_until: float | None,
) -> tuple[AlertStatus, float | None]:
    """State machine: return (new_status, resolved_until)."""
    if live_status in ACTIVE_STATUSES:
        return live_status, None

    clearing = (
        current_status in ACTIVE_STATUSES
        and live_status == AlertStatus.NO_ALERTS
    )
    if clearing:
        return AlertStatus.RESOLVED, time.monotonic() + RESOLVED_DURATION

    if current_status == AlertStatus.RESOLVED:
        if resolved_until is not None and time.monotonic() >= resolved_until:
            return AlertStatus.NO_ALERTS, None
        return current_status, resolved_until

    return AlertStatus.NO_ALERTS, None


BANNER = r"""
██████╗ ██╗██╗  ██╗██╗   ██╗██████╗
██╔══██╗██║██║ ██╔╝██║   ██║██╔══██╗
██████╔╝██║█████╔╝ ██║   ██║██║  ██║
██╔═══╝ ██║██╔═██╗ ██║   ██║██║  ██║
██║     ██║██║  ██╗╚██████╔╝██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝
Raspberry Pi × Pikud HaOref
"""


def main():
    logging.basicConfig(
        level=logging.WARNING, format="%(levelname)s: %(message)s"
    )

    print(BANNER)
    print(f"Monitoring city: {CITY}")
    print(f"Poll interval: {POLL_INTERVAL}s | Max backoff: {BACKOFF_MAX}s")
    print("-" * 50)

    led = AlertLED()
    session = requests.Session()

    # Seed session cookies the same way a browser would
    try:
        session.get(
            "https://www.oref.org.il/", headers=REQUEST_HEADERS, timeout=10
        )
    except Exception:
        pass

    print("-" * 50)

    current_status = AlertStatus.NO_ALERTS
    resolved_until: float | None = None
    backoff = 0
    first_poll = True

    # Startup ping: briefly flash RESOLVED on both outputs to confirm comms,
    # then let the first poll publish the real state
    print("Sending startup ping...")
    led.set_status(AlertStatus.RESOLVED)
    particle_notifier.publish(AlertStatus.RESOLVED, session)
    time.sleep(3)
    led.set_status(AlertStatus.NO_ALERTS)
    print("Startup ping done.")

    print(format_message(AlertStatus.NO_ALERTS, CITY, None))

    while True:
        if backoff > 0:
            time.sleep(backoff)
            backoff = 0

        try:
            alert_data = fetch_alerts(session)
            live_status, alert_info = resolve_status(alert_data, CITY)

            # When live is quiet, supplement with history to catch alerts
            # that disappeared from the live feed before cat-13 was issued
            if live_status == AlertStatus.NO_ALERTS:
                hist_status, hist_info = fetch_history_status(
                    session, CITY
                )
                if hist_status != AlertStatus.NO_ALERTS:
                    live_status, alert_info = hist_status, hist_info

            new_status, resolved_until = _compute_new_status(
                current_status, live_status, resolved_until
            )

            if new_status != current_status or first_poll:
                first_poll = False
                print(format_message(
                    new_status, CITY, alert_info, resolved_until
                ))
                current_status = new_status
                led.set_status(current_status)
                particle_notifier.publish(current_status, session)

        except requests.HTTPError as e:
            code = e.response.status_code if e.response is not None else "?"
            if code == 403:
                backoff = min(
                    (backoff * 2) if backoff else BACKOFF_BASE, BACKOFF_MAX
                )
                logging.warning(
                    f"403 Forbidden (geo-blocked?). Backing off {backoff}s."
                )
            else:
                logging.error(f"HTTP {code}: {e}")

        except requests.RequestException as e:
            backoff = min(
                (backoff * 2) if backoff else BACKOFF_BASE, BACKOFF_MAX
            )
            logging.error(f"Network error: {e}. Backing off {backoff}s.")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
