#!/usr/bin/env bash
# build.sh - compile Particle firmware to pikud.bin
#
# Usage: bash particle/scripts/build.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "==> Compiling firmware"
cd "$REPO_ROOT/particle"
particle compile photon . --saveTo "$REPO_ROOT/pikud.bin"

echo "Built: $REPO_ROOT/pikud.bin"
