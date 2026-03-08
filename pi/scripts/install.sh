#!/usr/bin/env bash
# install.sh - set up pikud on a Raspberry Pi
#
# Run once after cloning:
#   bash pi/scripts/install.sh
#
# Safe to re-run; every step is idempotent.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PI_DIR="${REPO_ROOT}/pi"
APP_DIR="${PI_DIR}/src"
APP_USER="$(whoami)"
VENV="${APP_DIR}/.venv"
SERVICE_NAME="pikud"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "==> Installing system packages"
sudo apt-get update -qq
sudo apt-get install -y python3 python3-venv python3-dev pigpio python3-rpi.gpio

echo "==> Enabling pigpiod"
sudo systemctl enable pigpiod
sudo systemctl start pigpiod || true

echo "==> Creating Python venv (with system-site-packages for GPIO)"
python3 -m venv --system-site-packages "$VENV"

echo "==> Installing Python dependencies"
"$VENV/bin/pip" install --quiet -r "$PI_DIR/requirements.txt"

echo "==> Checking .env"
if [ ! -f "$REPO_ROOT/.env" ]; then
    cat > "$REPO_ROOT/.env" <<EOF
PARTICLE_DEVICE_ID=""
PARTICLE_ACCESS_TOKEN=""
CITY="תל אביב"
PI_HOST=""
PI_USER="pi"
EOF
    echo "    Created .env - fill in your credentials before starting."
else
    echo "    .env already exists, skipping."
fi

echo "==> Installing systemd service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=PiKud - Pikud HaOref alert monitor
After=network-online.target pigpiod.service
Wants=network-online.target
Requires=pigpiod.service
StartLimitIntervalSec=0

[Service]
Type=simple
User=${APP_USER}
WorkingDirectory=${APP_DIR}
ExecStart=${VENV}/bin/python -u alerts.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

echo ""
echo "Done! Next steps:"
echo "  1. Edit .env with your Particle credentials and PI_HOST"
echo "  2. Set CITY in .env (default: תל אביב)"
echo "  3. sudo systemctl start $SERVICE_NAME"
echo "  4. journalctl -u $SERVICE_NAME -f"
