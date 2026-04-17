---
name: playwright-cli
description: >
  Automate browser interactions from the terminal using Playwright via CDP (Chrome
  DevTools Protocol). Use when you need to: open a browser, navigate to a URL,
  fill forms, click buttons, extract page data, take snapshots, handle dialogs,
  manage cookies/localStorage, mock network requests, record console output, or
  capture network traffic. Triggers: "open browser", "navigate to", "fill form",
  "click button", "scrape page", "extract data from page", "handle login",
  "mock API response", "record network traffic", "browser automation".
allowed-tools: Bash(playwright-cli *)
---

# playwright-cli

Playwright CLI backed by Chrome DevTools Protocol. Runs headless or headed, supports
multiple sessions, and persists cookies/localStorage across runs.

## Core Workflow

### Step 1: Open a browser session

```bash
playwright-cli open [url]
# or just
playwright-cli open
```

If no URL is given, opens an about:blank page. Use `goto` to navigate after.

**Sessions:** All commands target the active session. Use `-s=<session-name>` to
switch sessions (multiple browsers can run simultaneously):

```bash
playwright-cli -s=session2 open
playwright-cli -s=session2 goto https://example.com
```

### Step 2: Get element references

Before interacting, you need element refs. Take a snapshot:

```bash
playwright-cli snapshot
# Returns: element refs like e15, e22, etc.
```

Then use refs in interaction commands:
```bash
playwright-cli click e15       # click element ref e15
playwright-cli type "hello"    # type into the focused/input element
```

### Step 3: Navigate and interact

```bash
playwright-cli goto https://example.com/login
playwright-cli snapshot         # get fresh refs after navigation
playwright-cli fill e22 username
playwright-cli fill e23 password
playwright-cli click e24        # submit button
```

## Interaction Commands

| Command | Args | Description |
|---------|------|-------------|
| `open [url]` | URL (optional) | Open browser, optionally navigate to URL |
| `goto <url>` | URL | Navigate to URL |
| `click <ref>` | element ref | Left-click an element |
| `dblclick <ref>` | element ref | Double-click |
| `rightclick <ref>` | element ref | Right-click |
| `type <text>` | text | Type text into focused element |
| `fill <ref> <text>` | ref, text | Fill an input (clears first) |
| `hover <ref>` | element ref | Hover over element |
| `select <ref> <value>` | ref, value | Select dropdown option |
| `check <ref>` | element ref | Check a checkbox/radio |
| `uncheck <ref>` | element ref | Uncheck a checkbox |
| `upload <file>` | file path | Upload file(s) |
| `drag <refA> <refB>` | start, end | Drag element A to B |
| `press <key>` | key name | Press keyboard key (Enter, Tab, etc.) |
| `go-back` | — | Browser back |
| `go-forward` | — | Browser forward |
| `reload` | — | Reload current page |
| `snapshot` | — | Capture page → get element refs |
| `eval <code>` | JS code | Run JS on page, returns result |
| `eval <code> <ref>` | JS, ref | Run JS on specific element |

## State Commands

```bash
# Cookies
playwright-cli cookie-list
playwright-cli cookie-clear

# localStorage
playwright-cli localstorage-list
playwright-cli localstorage-get <key>
playwright-cli localstorage-set <key> <value>
playwright-cli localstorage-delete <key>

# Session data
playwright-cli delete-data   # clear all session data
```

## Network Mocking

```bash
# Mock API responses
playwright-cli route "*/api/users*"
playwright-cli route "*/api/*"    # catch-all

# List active mocks
playwright-cli route-list

# Remove mocks
playwright-cli unroute "*/api/users*"
playwright-cli unroute             # remove all
```

## Debugging Commands

```bash
# Console messages (errors, warnings, logs)
playwright-cli console [min-level]
# min-level: error | warn | log (default: log)

# Network requests since page load
playwright-cli network

# Run arbitrary Playwright JS code
playwright-cli run-code "page.title()"

# Show DevTools
playwright-cli show
playwright-cli devtools-start
```

## Recording

```bash
# Video recording
playwright-cli video-start
playwright-cli video-stop   # saves recording

# Trace recording (for Playwright trace viewer)
playwright-cli tracing-start
playwright-cli tracing-stop  # saves trace.zip, open with: npx playwright show-trace
```

## Session Management

```bash
# List all active sessions
playwright-cli list

# Close one or all sessions
playwright-cli close
playwright-cli close-all

# Force-kill zombie processes
playwright-cli kill-all
```

## Keyboard Shortcuts

```bash
playwright-cli press Enter
playwright-cli press Tab
playwright-cli press Escape
playwright-cli press ArrowDown
playwright-cli press Control+a
playwright-cli press Meta+k
```

## Common Patterns

### Login Flow
```bash
playwright-cli goto "https://example.com/login"
playwright-cli snapshot
playwright-cli fill e22 "myuser@example.com"
playwright-cli fill e23 "secretpass"
playwright-cli click e24
# Wait for redirect, then snapshot to verify
playwright-cli snapshot
```

### Extract page data
```bash
playwright-cli eval "document.querySelectorAll('.item').length"
playwright-cli eval "Array.from(document.querySelectorAll('h1')).map(h=>h.textContent)"
```

### Check element exists
```bash
playwright-cli snapshot
# Look for the ref in output
```

### Preserve login session
```bash
# After logging in, keep session alive for subsequent operations
playwright-cli localstorage-list   # verify session data stored
playwright-cli close              # close browser but session data persists
# Next open will restore localStorage
```

## Troubleshooting

- **"Element not found"** — run `snapshot` again; page may have changed after navigation
- **"Browser not running"** — run `playwright-cli open` first
- **Stale/zombie processes** — `playwright-cli kill-all` then restart
- **Upload not working** — use absolute path: `/home/user/file.pdf`
- **Session confusion** — use named sessions: `playwright-cli -s=work open`

## Install / Setup

```bash
playwright-cli install         # first-time setup (installs browsers)
playwright-cli install-browser # install just Chromium
```
