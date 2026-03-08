# Raspberry Pi Setup

## Hardware

- Raspberry Pi (any model with 40-pin header; tested on Pi 1)
- 5mm RGB LED (common cathode)
- Resistors: 150 Ω × 2 (R, G), 33 Ω × 1 (B)
- Breadboard + jumper wires
- WiFi or ethernet

See [WIRING.md](WIRING.md) for the full wiring diagram.

---

## Software setup

### 1. Clone the repo

```bash
git clone <repo-url> ~/pikud
cd ~/pikud
```

### 2. Run the install script

```bash
bash pi/scripts/install.sh
```

This will:
- Install system packages (`python3`, `python3-dev`, `pigpio`, `RPi.GPIO`)
- Enable and start `pigpiod`
- Create a Python venv at `pi/src/.venv/` with system-site-packages
- Install Python dependencies
- Create a blank `.env` if one doesn't exist
- Install and enable the `pikud` systemd service

### 3. Configure credentials

Edit `.env`:

```
PARTICLE_DEVICE_ID="your-device-id"
PARTICLE_ACCESS_TOKEN="your-token"
```

Get these via the Particle CLI — see [PARTICLE.md](PARTICLE.md) for details.

### 4. Set your city (optional)

Set `CITY` in `.env` - the name must exactly match what the oref API
returns (Hebrew). Default: `תל אביב` (Tel Aviv).

### 5. Start the service

```bash
sudo systemctl start pikud
```

---

## Managing the service

| Command | Description |
|---------|-------------|
| `sudo systemctl start pikud` | Start |
| `sudo systemctl stop pikud` | Stop |
| `sudo systemctl restart pikud` | Restart |
| `sudo systemctl status pikud` | Status |
| `journalctl -u pikud -f` | Live log output |
| `journalctl -u pikud -n 100` | Last 100 log lines |
| `sudo systemctl disable pikud` | Disable autostart |

---

## Updating

```bash
git pull
bash pi/scripts/install.sh   # re-installs deps and updates service file
sudo systemctl restart pikud
```

Or deploy remotely from your dev machine (requires `PI_HOST` in `.env`):

```bash
bash pi/scripts/deploy.sh
```

---

## Testing the LED without a real alert

```bash
# Install venv if needed
pi/src/.venv/bin/python pi/src/test_led.py
```

Cycles through all four states (yellow → red → blue → off) for 4
seconds each.

---

## Troubleshooting

**LED not lighting up**
- Check wiring against [WIRING.md](WIRING.md)
- Confirm `pigpiod` is running: `sudo systemctl status pigpiod`
- Run the static GPIO test:

```bash
python3 -c "
import RPi.GPIO as GPIO, time
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.HIGH)
time.sleep(5)
GPIO.cleanup()
"
```

**Service not starting**
- Check logs: `journalctl -u pikud -n 50`
- Confirm `.env` has valid credentials
- Confirm WiFi is up before the service starts (it will retry every 30s)

**Always showing wrong status**
- The script checks the live oref API and falls back to history
- History is checked within a 30-minute window
- If you're outside Israel the live API will return 403 (geo-blocked)
  - the service backs off automatically
