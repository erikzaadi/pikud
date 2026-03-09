"""
RGB LED controller for Raspberry Pi GPIO.

Wiring (BCM pin numbers, common-cathode LED):
  R pin  → 150Ω → GPIO 17  (board pin 11)
  GND    → direct → GND    (board pin 6)
  G pin  → 150Ω → GPIO 27  (board pin 13)
  B pin  →  33Ω → GPIO 22  (board pin 15)
"""

import threading
import time
import logging

# gpiozero is pre-installed on Raspberry Pi OS.
# On other systems (dev/test) import will fail - LED is silently disabled.
try:
    from gpiozero import RGBLED
    from gpiozero.pins.pigpio import PiGPIOFactory
    _GPIO_AVAILABLE = True
except Exception:
    _GPIO_AVAILABLE = False

PIN_RED = 17
PIN_GREEN = 27
PIN_BLUE = 22

PULSE_PERIOD = 4.0  # seconds per full pulse cycle

# (r, g, b) as 0.0–1.0 fractions; None = off
_COLORS = {
    "no_alerts":   None,
    "pre_warning": (1.0, 1.0, 0.0),  # yellow - get near shelter
    "alert":       (1.0, 0.0, 0.0),  # red    - go to shelter now
    "resolved":    (0.0, 0.0, 1.0),  # blue   - cooling down
}


class AlertLED:
    def __init__(self):
        self._status = "no_alerts"
        self._lock = threading.Lock()
        self._led = None

        if not _GPIO_AVAILABLE:
            logging.warning("gpiozero not available - GPIO LED disabled")
            return

        try:
            factory = PiGPIOFactory()
            self._led = RGBLED(
                red=PIN_RED, green=PIN_GREEN, blue=PIN_BLUE,
                pin_factory=factory,
            )
            # Pre-initialize PWM on all channels so pigpio doesn't raise
            # 'GPIO is not in use for PWM' on the first off() call.
            for pin_num in (PIN_RED, PIN_GREEN, PIN_BLUE):
                factory.connection.set_PWM_dutycycle(pin_num, 0)
        except Exception as e:
            logging.warning(f"GPIO LED init failed: {e}")
            return

        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def set_status(self, status) -> None:
        """Call this whenever the alert status changes."""
        with self._lock:
            self._status = status.value if hasattr(status, "value") else status

    def _run(self) -> None:
        while True:
            with self._lock:
                status = self._status

            color = _COLORS.get(status)

            if color is None:
                self._led.off()
                time.sleep(0.05)
            else:
                phase = time.monotonic() % PULSE_PERIOD
                if phase < PULSE_PERIOD / 2:
                    brightness = phase / (PULSE_PERIOD / 2)
                else:
                    brightness = (PULSE_PERIOD - phase) / (PULSE_PERIOD / 2)

                self._led.value = (
                    color[0] * brightness,
                    color[1] * brightness,
                    color[2] * brightness,
                )
                time.sleep(0.01)  # ~100 fps
