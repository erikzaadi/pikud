# CLAUDE.md

## Linting

After editing any Python file in `pi/src/`, run all three linters and fix any issues before finishing:

```bash
pi/src/.venv/bin/python -m pycodestyle pi/src/
pi/src/.venv/bin/python -m pyflakes pi/src/
pi/src/.venv/bin/python -m mypy --ignore-missing-imports pi/src/
```

Rules (configured in `pi/setup.cfg`):
- Max line length: **79 characters**
- mypy: `ignore_missing_imports = True`

If the venv doesn't exist yet:
```bash
python3 -m venv --system-site-packages pi/src/.venv
pi/src/.venv/bin/pip install requests python-dotenv gpiozero pigpio types-requests pycodestyle pyflakes mypy
```

Note: always use `--system-site-packages` when creating the venv — required for GPIO access on the Pi.

## Deploying to the Pi

```bash
bash pi/scripts/remote_install.sh   # full sync + reinstall (first time or after dep changes)
bash pi/scripts/deploy.sh           # rsync + restart (day-to-day)
bash pi/scripts/logs.sh             # tail live logs
```

Requires `PI_HOST` (and optionally `PI_USER`) set in `.env`.
