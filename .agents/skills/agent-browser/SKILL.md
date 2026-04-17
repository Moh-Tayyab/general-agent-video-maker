---
name: agent-browser
description: >
  Full-featured browser automation CLI for AI agents. Automates Chrome/Chromium via CDP
  for any web task: form filling, data extraction, login flows, network mocking, PDF
  generation, tab management, and more. Also supports Electron desktop apps (VS Code,
  Slack, Discord, Figma, Notion), Slack workspace interaction, Vercel Sandbox microVMs,
  and AWS Bedrock AgentCore cloud browsers. Triggers: "open a website", "fill out a form",
  "click a button", "scrape data", "extract from page", "test this web app", "login to
  site", "automate browser actions", "automate Electron app", "check Slack", "send Slack
  message", "run browser in cloud", "browser recording", "compare page snapshots".
allowed-tools: Bash(npx agent-browser:*)
---

# agent-browser

Full Chrome/Chromium browser automation via CDP. Covers every workflow: navigation,
interaction, state, network, sessions, debugging, plus Electron/Slack/Vercel/Bedrock
extensions.

## Installation

```bash
npm i -g agent-browser
agent-browser install   # first time: install Chromium
```

All commands below use `npx agent-browser` (or `agent-browser` if installed globally).

---

## Core Workflow

### Step 1: Open a page

```bash
agent-browser open <url>
# Example:
agent-browser open https://github.com/login
```

### Step 2: Inspect page state

```bash
agent-browser snapshot           # accessibility tree → element refs
agent-browser screenshot         # visual screenshot
agent-browser title              # page title
agent-browser url                # current URL
agent-browser text              # all visible text
agent-browser html              # full HTML
```

### Step 3: Interact using refs

```bash
agent-browser snapshot           # get refs like @a3, #b7, button:c12
agent-browser click #b7          # click element with ref #b7
agent-browser type @a3 "hello"   # type into input
agent-browser fill @a3 "hello"    # fill (clears first)
agent-browser press Enter        # keyboard
agent-browser wait 2000          # pause (ms) or @selector
```

---

## All Interaction Commands

| Command | Example | Description |
|---------|---------|-------------|
| `open <url>` | `open https://example.com` | Navigate to URL |
| `click <sel>` | `click #login-btn` | Click element (ref format below) |
| `dblclick <sel>` | `dblclick .item` | Double-click |
| `type <sel> <text>` | `type input[name=user] "me"` | Type into focused element |
| `fill <sel> <text>` | `fill #password "secret"` | Clear + fill input |
| `press <key>` | `press Tab` | Press keyboard key |
| `keyboard type <text>` | `keyboard type "hello world"` | Real keystroke typing |
| `hover <sel>` | `hover .menu-item` | Hover over element |
| `focus <sel>` | `focus #search` | Focus element |
| `check <sel>` | `check .agree-checkbox` | Check checkbox/radio |
| `uncheck <sel>` | `uncheck #opt-in` | Uncheck |
| `select <sel> <val>` | `select #country "US"` | Dropdown select |
| `drag <src> <dst>` | `drag .handle .drop-zone` | Drag element |
| `upload <sel> <files...>` | `upload input[type=file] /tmp/file.pdf` | File upload |
| `download <sel> <path>` | `download a[download] /tmp/` | Download via click |
| `scroll <dir> [px]` | `scroll down 300` | Scroll page |
| `scrollintoview <sel>` | `scrollintoview #footer` | Scroll element into view |
| `wait <sel\|ms>` | `wait @submit-btn` | Wait for element or ms |

### Element Selectors

```
@a3           → ref from last snapshot
#b7           → ref from last snapshot
button:c12    → by role + count
input[name=x] → CSS selector
text:"Log in" → text content match
@text:"Log in" → exact text match
```

---

## State Queries

```bash
agent-browser text                    # all visible text
agent-browser html                    # full HTML
agent-browser value <sel>            # input/select value
agent-browser attr <sel> <name>       # get attribute
agent-browser title                  # page title
agent-browser url                    # current URL
agent-browser count <sel>            # count matching elements
agent-browser box <sel>              # element bounding box {x,y,w,h}
agent-browser styles <sel>           # computed CSS styles
agent-browser visible <sel>          # true/false
agent-browser enabled <sel>          # true/false
agent-browser role <sel>            # ARIA role
agent-browser label <sel>            # associated label text
agent-browser cdp-url                # get CDP WebSocket URL
```

---

## Session Management / Tabs

```bash
agent-browser tab new               # open new tab
agent-browser tab list               # list all tabs
agent-browser tab close              # close current tab
agent-browser tab 2                 # switch to tab 2
agent-browser back                  # browser back
agent-browser forward               # browser forward
agent-browser reload                # reload page
agent-browser close                 # close current browser
agent-browser close --all           # close ALL browser sessions
```

---

## Network

```bash
agent-browser requests              # list all network requests
agent-browser requests --clear      # clear request log
agent-browser route <url> --abort   # abort requests matching URL
agent-browser route <url> --body '{"error":"mocked"}'  # mock response
agent-browser unroute <url>        # remove mock
agent-browser unroute              # remove all mocks
agent-browser har start [path]     # start HAR recording
agent-browser har stop /tmp.har     # stop and save
agent-browser offline [on|off]      # toggle offline mode
agent-browser headers <json>        # set request headers
agent-browser credentials <user> <pass>  # set auth credentials
```

---

## Cookies & Storage

```bash
agent-browser cookies get           # get all cookies
agent-browser cookies set --url https://example.com --name token --value abc123
agent-browser cookies clear
agent-browser storage local         # list localStorage
agent-browser storage session       # list sessionStorage
agent-browser storage local set <key> <value>
agent-browser storage local get <key>
agent-browser storage local clear
```

---

## Viewport & Environment

```bash
agent-browser viewport 1280 720    # set viewport size
agent-browser viewport device iPhone  # emulate device
agent-browser geo 37.7749 -122.4194  # mock geolocation
agent-browser offline on            # simulate offline
agent-browser media dark            # prefers-color-scheme: dark
agent-browser media light
agent-browser media reduced-motion  # prefers-reduced-motion
```

---

## PDF & Screenshots

```bash
agent-browser screenshot                    # save screenshot
agent-browser screenshot /tmp/page.png
agent-browser pdf /tmp/page.pdf            # save as PDF
```

---

## Advanced

### Run JavaScript on page

```bash
agent-browser eval "document.title"
agent-browser eval "JSON.stringify([...document.querySelectorAll('h1')].map(h=>h.textContent))"
```

### Compare page states

```bash
agent-browser snapshot
# make some changes...
agent-browser diff snapshot          # compare accessibility trees
agent-browser diff screenshot         # compare screenshots
agent-browser diff url <url1> <url2>  # compare two URLs
```

### Recording

```bash
agent-browser trace start /tmp/trace.zip
# ... perform actions ...
agent-browser trace stop             # save trace.zip
# View: npx playwright show-trace /tmp/trace.zip

agent-browser profiler start /tmp/profile.json
agent-browser profiler stop

agent-browser record start /tmp/video.webm
agent-browser record stop
```

### Console & Debugging

```bash
agent-browser console               # view console logs
agent-browser console --clear
agent-browser show                   # open DevTools
agent-browser devtools-start
agent-browser connect <port>         # connect to existing browser
agent-browser connect <ws-url>     # connect via WebSocket
```

---

## Built-in Skills

Run `npx agent-browser skills` to see available skill packs. Load one before using it:

```bash
agent-browser skills get electron    # automate VS Code, Slack, Discord, Figma
agent-browser skills get slack        # Slack-specific commands
agent-browser skills get vercel-sandbox  # run in Vercel microVMs
agent-browser skills get dogfood     # systematic UX testing
```

---

## Example: Complete Login Flow

```bash
agent-browser open https://app.example.com/login
agent-browser snapshot
agent-browser fill input[name=email] "user@example.com"
agent-browser fill input[name=password] "secret123"
agent-browser click button[type=submit]
agent-browser wait @dashboard-view     # wait for redirect
agent-browser snapshot                 # verify success
```

---

## Troubleshooting

- **"Browser not running"** → `agent-browser open` first
- **Wrong element clicked** → run `snapshot` after every navigation
- **Stale element** → `scrollintoview <sel>` then retry
- **Zombie processes** → `agent-browser close --all`
- **Install issues** → `npm i -g agent-browser && agent-browser install`
