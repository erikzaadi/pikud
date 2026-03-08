#!/usr/bin/env python3
"""
Quick GPIO LED test - cycles through all alert colours so you can verify
each channel (R, G, B) and the pulse effect work correctly.

Run on the Pi:
    python test_led.py
"""

import time
from gpio_led import AlertLED
from alerts import AlertStatus

STEPS = [
    (AlertStatus.PRE_WARNING, "PRE_WARNING - yellow (get near shelter)"),
    (AlertStatus.ALERT,       "ALERT       - red    (go to shelter now)"),
    (AlertStatus.RESOLVED,    "RESOLVED    - blue   (cooling down)"),
    (AlertStatus.NO_ALERTS,   "NO_ALERTS   - off"),
]

HOLD_SECONDS = 4  # how long to show each colour


def main():
    led = AlertLED()
    print("LED test starting - press Ctrl+C to abort\n")

    for status, label in STEPS:
        print(f"  {label}")
        led.set_status(status)
        time.sleep(HOLD_SECONDS)

    print("\nDone.")


if __name__ == "__main__":
    main()
