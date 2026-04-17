#!/usr/bin/env bash
# =============================================================================
# bootlogix-hooks/stop.sh — Run when Claude Code session ENDS
# =============================================================================
# Saves session memory so the next session can warm up instantly.
#
# Trigger: fires when Claude Code session terminates
# =============================================================================

set -euo pipefail

HOOK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
# shellcheck source=/home/muhammad_tayyab/bootlogix/.claude/hooks/lib.sh
source "$HOOK_SCRIPT_DIR/lib.sh"

log_info "bootlogix hooks: stop sequence beginning"

# ---------------------------------------------------------------------------
# 1. Save session snapshot to memory
# ---------------------------------------------------------------------------
bootlogix_session_save "session-$(date '+%Y%m%d-%H%M%S')"

# ---------------------------------------------------------------------------
# 2. Capture git status (uncommitted work context)
# ---------------------------------------------------------------------------
git_status_file="$BOOTLOGIX_MEMORY_DIR/git-status.md"
mkdir -p "$BOOTLOGIX_MEMORY_DIR"

git_branch=$(git -C "$BOOTLOGIX_PROJECT_DIR" branch --show-current 2>/dev/null || echo "unknown")
git_status=$(git -C "$BOOTLOGIX_PROJECT_DIR" status --short 2>/dev/null | head -50 || true)

cat > "$git_status_file" << EOF
# Git Status Snapshot

Captured: $(date '+%Y-%m-%d %H:%M:%S')

## Branch: $git_branch

## Status:
\`\`\`
$git_status
\`\`\`
EOF

log_info "Git status snapshot saved"

# ---------------------------------------------------------------------------
# 3. Clean up temp files (keeps workspace tidy)
# ---------------------------------------------------------------------------
if [[ -d "$BOOTLOGIX_TEMP_DIR" ]]; then
  find "$BOOTLOGIX_TEMP_DIR" -type f -mtime +7 -delete 2>/dev/null || true
  log_info "Temp files older than 7 days cleaned"
fi

log_info "bootlogix hooks: stop sequence complete"
