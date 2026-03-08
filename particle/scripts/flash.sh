#!/usr/bin/env bash
# flash.sh - compile and flash firmware to Photon via OTA
#
# Requires PARTICLE_DEVICE_ID in .env
#
# Usage: bash particle/scripts/flash.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/.env"

echo "==> Flashing to device $PARTICLE_DEVICE_ID"
cd "$REPO_ROOT/particle"
particle flash --cloud "$PARTICLE_DEVICE_ID" .
