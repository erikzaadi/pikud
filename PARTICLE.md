# Particle Photon Setup

## Prerequisites

- [Particle CLI](https://docs.particle.io/getting-started/developer-tools/cli/)
  installed and logged in
- A Particle account with the Photon claimed to it

```bash
npm install -g particle-cli
# or 
bash <( curl -sL https://particle.io/install-cli )

particle login

# Get credentials for .env
particle token create      # → PARTICLE_ACCESS_TOKEN
particle list              # → PARTICLE_DEVICE_ID
```

---

## Build & flash

```bash
# Compile + flash in one step (OTA, device must be online)
bash particle/scripts/flash.sh

# Or compile first, then flash separately
bash particle/scripts/build.sh
source .env && particle flash --cloud $PARTICLE_DEVICE_ID pikud.bin
```

---

## LED colours

| Status | Colour | Meaning |
|--------|--------|---------|
| `no_alerts` | Off | No active alerts |
| `pre_warning` | Pulsing yellow | Alerts expected soon - get near shelter |
| `alert` | Pulsing red | Active alert - go to shelter now |
| `resolved` | Pulsing blue | Alert cleared - 5 min cooldown |

---

## Testing without a real alert

### Subscribe to cloud events (no USB needed)

```bash
bash particle/scripts/monitor.sh
```

### Watch serial output (USB)

```bash
particle serial monitor --follow
```

### Simulate a status (same path as the Pi)

```bash
bash particle/scripts/simulate.sh pre_warning
bash particle/scripts/simulate.sh alert
bash particle/scripts/simulate.sh resolved
bash particle/scripts/simulate.sh no_alerts
```

> **Tip:** temporarily set `RESOLVED_DURATION_MS = 15000` in
> `particle/src/pikud.ino` while testing so the 5-minute cooldown is only
> 15 seconds.

---

## Debugging

### Serial log shows reset reason on every boot

```
Reset reason: 0 (other)  free mem: 50816
Waiting for alert_status events from Pi...
```

Reset reasons to watch out for:

| Code | Reason | Action |
|------|--------|--------|
| `watchdog` | Firmware hung | Check for blocking code |
| `panic/fault` | Assert failed | Usually a Device OS version mismatch - run `particle update` |
| `power down` | Normal power cycle | - |

### Device flashing red LED / serial disconnecting

This usually means a panic or assert failure. Fix:

```bash
# Put device in DFU mode: hold SETUP, tap RESET,
# release SETUP when LED blinks yellow
particle update          # update Device OS
particle flash --usb pikud.bin
```

### OTA flash not reaching device

- Confirm device is online: `particle list`
- Check Particle console → device → last handshake
- Try USB flash instead: `particle flash --usb pikud.bin`

### Photon stuck showing old status after Pi restarts

The Pi sends a startup ping (blue flash) followed by the real status
on the first poll (~10 seconds). If the Photon shows blue after startup
and doesn't update, check the Pi logs:

```bash
journalctl -u pikud -f
```

---

## Updating firmware

```bash
bash particle/scripts/flash.sh
```
