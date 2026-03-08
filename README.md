```
██████╗ ██╗██╗  ██╗██╗   ██╗██████╗
██╔══██╗██║██║ ██╔╝██║   ██║██╔══██╗
██████╔╝██║█████╔╝ ██║   ██║██║  ██║
██╔═══╝ ██║██╔═██╗ ██║   ██║██║  ██║
██║     ██║██║  ██╗╚██████╔╝██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝
```

*Raspberry Pi × Pikud HaOref - monitors Israeli Home Front Command alerts and drives an RGB LED*

[Why this exists →](STORY.md)

---

> **⚠️ Disclaimer**
> This is a personal hobby project and is **not** an official product of Pikud HaOref or any government body.
> It is **not** a substitute for the official Home Front Command app, sirens, or any authorised alert system.
> Always follow official guidance. Your phone and the sirens come first.

---

## Architecture

```
Pi (alerts.py)
  polls oref API (Israel)
  handles state machine
  drives RGB LED via GPIO

  [optional] → Particle cloud → Photon → drives a second LED remotely
```

The Pi does all the work, it polls the geo-blocked oref API, tracks state, and drives the local RGB LED. Particle cloud integration is optional: if `PARTICLE_DEVICE_ID` and `PARTICLE_ACCESS_TOKEN` are set in `.env`, status changes are also pushed to a Particle Photon.

---

## Raspberry Pi setup

```bash
bash pi/scripts/install.sh   # creates venv, installs deps, registers systemd service
sudo systemctl start pikud
journalctl -u pikud -f
```

See [RASPBERRY_PI.md](RASPBERRY_PI.md) for full setup, config, and troubleshooting.

---

## Particle Photon *(optional)* - `particle/src/pikud.ino`

```bash
bash particle/scripts/flash.sh   # compile + flash in one step
```

See [PARTICLE.md](PARTICLE.md) for build, flash, testing, and LED colour reference.
