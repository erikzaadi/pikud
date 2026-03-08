#!/usr/bin/env bash
# remote_install.sh - copy repo to the Raspberry Pi and run the install script
#
# Syncs pi/, .env, and .env.example to ~/pikud on the Pi, then runs
# pi/scripts/install.sh remotely.
#
# Requires PI_HOST in .env (PI_USER defaults to "pi")
#
# Usage: bash pi/scripts/remote_install.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/.env"

PI_USER="${PI_USER:-pi}"
REMOTE="${PI_USER}@${PI_HOST}"
REMOTE_DIR="${REMOTE_DIR:-~/pikud}"

echo "==> Preparing ${REMOTE_DIR} on ${REMOTE}"
ssh "${REMOTE}" "mkdir -p ${REMOTE_DIR}/pi/src ${REMOTE_DIR}/pi/scripts"

echo "==> Syncing files to ${REMOTE}:${REMOTE_DIR}"
rsync -avz \
    --exclude-from="$REPO_ROOT/.gitignore" \
    "$REPO_ROOT/pi/" \
    "${REMOTE}:${REMOTE_DIR}/pi/"

rsync -avz \
    "$REPO_ROOT/.env" \
    "$REPO_ROOT/.env.example" \
    "${REMOTE}:${REMOTE_DIR}/"

echo "==> Running install script on ${REMOTE}"
ssh "${REMOTE}" "bash ${REMOTE_DIR}/pi/scripts/install.sh"

echo "==> Starting pikud service"
ssh "${REMOTE}" "sudo systemctl start pikud"

echo "Done - pikud is running on ${REMOTE}"
