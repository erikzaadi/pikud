#!/usr/bin/env bash
# wifi_watchdog.sh - restart wlan0 if the gateway is unreachable
#
# Intended to run as a systemd timer every few minutes.
# Logs to syslog via logger.

set -euo pipefail

IFACE="wlan0"
PING_COUNT=3
PING_TIMEOUT=5  # seconds per ping

GATEWAY=$(ip route show dev "$IFACE" 2>/dev/null \
    | awk '/default/ {print $3; exit}')

if [ -z "$GATEWAY" ]; then
    logger -t wifi_watchdog "No gateway found on $IFACE - skipping"
    exit 0
fi

if ping -c "$PING_COUNT" -W "$PING_TIMEOUT" -I "$IFACE" \
        "$GATEWAY" > /dev/null 2>&1; then
    exit 0
fi

logger -t wifi_watchdog \
    "Gateway $GATEWAY unreachable on $IFACE - restarting interface"

ip link set "$IFACE" down
sleep 2
ip link set "$IFACE" up

logger -t wifi_watchdog "Interface $IFACE restarted"
