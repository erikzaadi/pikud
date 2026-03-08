#!/usr/bin/env bash
# logs.sh - follow pikud service logs on the Raspberry Pi via SSH
#
# Requires PI_HOST in .env (PI_USER defaults to "pi")
#
# Usage: bash pi/scripts/logs.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/.env"

PI_USER="${PI_USER:-pi}"
REMOTE="${PI_USER}@${PI_HOST}"

exec ssh "${REMOTE}" "journalctl -u pikud -f"
