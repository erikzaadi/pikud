#!/usr/bin/env bash
# watchdog_logs.sh - follow WiFi watchdog logs on the Raspberry Pi via SSH
#
# Requires PI_HOST in .env (PI_USER defaults to "pi")
#
# Usage: bash pi/scripts/watchdog_logs.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/.env"

PI_USER="${PI_USER:-pi}"
REMOTE="${PI_USER}@${PI_HOST}"

exec ssh "${REMOTE}" "journalctl -t wifi_watchdog -f"
