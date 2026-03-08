#!/usr/bin/env bash
# monitor.sh - subscribe to alert_status events from the Particle cloud
#
# Works without USB - shows events published by the Pi in real time.
# Ctrl+C to stop.
#
# Usage: bash particle/scripts/monitor.sh

set -euo pipefail

particle subscribe alert_status
