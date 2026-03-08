#!/usr/bin/env bash
# deploy.sh - rsync Pi source to the Raspberry Pi and restart the service
#
# Requires PI_HOST in .env (PI_USER defaults to "pi")
#
# Usage: bash pi/scripts/deploy.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/.env"

PI_USER="${PI_USER:-pi}"
REMOTE="${PI_USER}@${PI_HOST}"
REMOTE_DIR="${REMOTE_DIR:-~/pikud}"

echo "==> Syncing pi/src/ to ${REMOTE}:${REMOTE_DIR}"
rsync -avz --exclude '__pycache__' --exclude '.venv' \
    "$REPO_ROOT/pi/src/" \
    "${REMOTE}:${REMOTE_DIR}/pi/src/"

echo "==> Restarting pikud service"
ssh "${REMOTE}" "sudo systemctl restart pikud"

echo "Done - pikud restarted on ${REMOTE}"
