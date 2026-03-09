#!/usr/bin/env bash
# simulate.sh - inject a test alert status into the Particle Photon
#
# Requires PARTICLE_DEVICE_ID in .env
#
# Usage: bash particle/scripts/simulate.sh <status>
#
# Valid statuses: no_alerts, pre_warning, alert, resolved

set -euo pipefail

VALID_STATUSES="no_alerts pre_warning alert resolved"

usage() {
    echo "Usage: bash particle/scripts/simulate.sh <status>"
    echo "Valid statuses: $VALID_STATUSES"
    exit 1
}

STATUS="${1:-}"

if [ -z "$STATUS" ]; then
    echo "Error: status is required"
    usage
fi

valid=false
for s in $VALID_STATUSES; do
    if [ "$STATUS" = "$s" ]; then
        valid=true
        break
    fi
done

if [ "$valid" = false ]; then
    echo "Error: invalid status '$STATUS'"
    usage
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/.env"

echo "==> Publishing alert_status '$STATUS' to device $PARTICLE_DEVICE_ID"
particle publish alert_status "$STATUS"
