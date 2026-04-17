#!/usr/bin/env bash
# =============================================================================
# bootlogix-hooks/watch.sh — Watch-folder daemon starter
# =============================================================================
# Sets up inotifywait watch on the configured drop folder. When a video file
# lands, it triggers the SSD pipeline callback.
#
# This is a DAEMON script — it blocks forever. Run it in the background.
# The stop.sh hook handles cleanup.
#
# Default watch folder: ~/bootlogix-drops (configurable via WATCH_DIR env)
# =============================================================================

set -euo pipefail

HOOK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$HOOK_SCRIPT_DIR/lib.sh"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WATCH_DIR="${WATCH_DIR:-$HOME/bootlogix-drops}"
CALLBACK_SCRIPT="$HOOK_SCRIPT_DIR/watch-callback.sh"
PID_FILE="$BOOTLOGIX_TEMP_DIR/watch-folder.pid"

mkdir -p "$WATCH_DIR"
mkdir -p "$BOOTLOGIX_TEMP_DIR"

log_info "Watch-folder daemon starting — monitoring: $WATCH_DIR"

# ---------------------------------------------------------------------------
# Daemonize: write PID and redirect I/O
# ---------------------------------------------------------------------------
exec 1>>"$BOOTLOGIX_TEMP_DIR/watch-folder.log"
exec 2>&1

echo $$ > "$PID_FILE"

# ---------------------------------------------------------------------------
# Watch loop — blocks on inotifywait, fires callback on file drops
# ---------------------------------------------------------------------------
bootlogix_watch_folder "$WATCH_DIR" "$CALLBACK_SCRIPT"
