#!/usr/bin/env bash
# test_led.sh - run the LED test cycle on the Raspberry Pi via SSH
#
# Cycles through all alert colours (yellow, red, blue, off) for 4s each.
# Requires PI_HOST in .env (PI_USER defaults to "pi")
#
# Usage: bash pi/scripts/test_led.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/.env"

PI_USER="${PI_USER:-pi}"
REMOTE="${PI_USER}@${PI_HOST}"

ssh "${REMOTE}" "bash -s" <<'EOF'
set -euo pipefail

SERVICE_WAS_RUNNING=false
if systemctl is-active --quiet pikud; then
    echo "==> Stopping pikud service"
    sudo systemctl stop pikud
    SERVICE_WAS_RUNNING=true
fi

cd ~/pikud/pi/src && .venv/bin/python test_led.py

if [ "$SERVICE_WAS_RUNNING" = true ]; then
    echo "==> Restarting pikud service"
    sudo systemctl start pikud
fi
EOF
