#!/usr/bin/env bash
# =============================================================================
# bootlogix-hooks/pretooluse.sh — Security gate: run BEFORE every tool
# =============================================================================
# Blocks dangerous operations and validates credential safety.
# This is the MOST IMPORTANT hook — prevents credential leaks.
#
# Trigger: fires before ANY tool execution (bash, read, edit, write, etc.)
# Fail action: exits non-zero → tool is blocked
# Pass action: exits zero → tool proceeds
#
# Claude Code hook entry: reads JSON on stdin with tool_name + tool_args
# =============================================================================

set -euo pipefail

# Source shared library
HOOK_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
# shellcheck source=/home/muhammad_tayyab/bootlogix/.claude/hooks/lib.sh
source "$HOOK_SCRIPT_DIR/lib.sh"

# ---------------------------------------------------------------------------
# Parse stdin JSON from Claude Code
# ---------------------------------------------------------------------------
parse_input() {
  local input
  input=$(cat)
  TOOL_NAME=$(echo "$input" | grep -o '"tool_name":"[^"]*"' | sed 's/"tool_name":"//;s/"$//')
  TOOL_ARGS=$(echo "$input" | grep -o '"tool_args":"[^"]*"' | sed 's/"tool_args":"//;s/"$//' || echo "")
}

# ---------------------------------------------------------------------------
# Main gate logic
# ---------------------------------------------------------------------------
main() {
  # Load credentials so we can check token freshness
  bootlogix_load_credentials

  log_debug "pretooluse: tool='$TOOL_NAME'"

  # -----------------------------------------------------------------------
  # Gate 1: BLOCK git push --force (can destroy remote history)
  # -----------------------------------------------------------------------
  if [[ "$TOOL_NAME" == "Bash" ]] && echo "$TOOL_ARGS" | grep -qE "git\s+push\s+.*--force"; then
    log_error "BLOCKED: git push --force would destroy remote history"
    log_error "Use 'git push --force-with-lease' instead for safety"
    exit 1
  fi

  # -----------------------------------------------------------------------
  # Gate 2: BLOCK dangerous file deletions outside /tmp
  # -----------------------------------------------------------------------
  if [[ "$TOOL_NAME" == "Bash" ]]; then
    # Block: rm -rf / of any form (accidental or intentional)
    if echo "$TOOL_ARGS" | grep -qE "rm\s+(-[rf]+\s+)?/(\s|$)"; then
      log_error "BLOCKED: rm -rf / detected — catastrophic operation"
      exit 1
    fi
    # Block: git reset --hard (destroys uncommitted work)
    if echo "$TOOL_ARGS" | grep -qE "git\s+reset\s+--hard"; then
      log_error "BLOCKED: git reset --hard destroys uncommitted changes"
      log_error "Use 'git stash' or 'git reset --keep' instead"
      exit 1
    fi
    # Block: git clean -fd (removes untracked files permanently)
    if echo "$TOOL_ARGS" | grep -qE "git\s+clean\s+-[fd]+"; then
      log_error "BLOCKED: git clean removes untracked files permanently"
      exit 1
    fi
  fi

  # -----------------------------------------------------------------------
  # Gate 3: SECRETS SCAN on file write targets
  # -----------------------------------------------------------------------
  if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" || "$TOOL_NAME" == "Bash" ]]; then
    local potential_files
    potential_files=$(echo "$TOOL_ARGS" | grep -oE '"file_path":\s*"[^"]*"' | sed 's/"file_path":\s*"//;s/"$//g' || true)
    potential_files+=$'\n'
    potential_files+=$(echo "$TOOL_ARGS" | grep -oE '(^|/)[a-zA-Z0-9._-]+(/[a-zA-Z0-9._-]+)*' | grep -vE '^(git|curl|wget|npm|node|python)' || true)

    while IFS= read -r file; do
      [[ -z "$file" ]] && continue
      case "$file" in
        /tmp/*|/proc/*|/sys/*|/dev/*) continue ;;
      esac
      if [[ -f "$file" ]] && bootlogix_detect_secrets "$file"; then
        log_error "BLOCKED: file '$file' contains secrets"
        exit 1
      fi
    done <<< "$potential_files"
  fi

  # -----------------------------------------------------------------------
  # Gate 4: CREDENTIAL freshness check (warn if tokens expiring soon)
  # -----------------------------------------------------------------------
  if ! bootlogix_check_token_freshness 86400; then
    log_warn "Credential freshness check failed — tokens may need refresh"
  fi

  # -----------------------------------------------------------------------
  # Gate 5: BLOCK .env commit in git (common mistake)
  # -----------------------------------------------------------------------
  if [[ "$TOOL_NAME" == "Bash" ]] && echo "$TOOL_ARGS" | grep -qE "git\s+add.*\.env"; then
    log_error "BLOCKED: staging .env file risks committing secrets"
    exit 1
  fi

  exit 0
}

# Entry point — parse input then run gates
parse_input
main
