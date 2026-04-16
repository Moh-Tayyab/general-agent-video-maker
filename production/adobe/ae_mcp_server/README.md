# After Effects MCP Server Setup

> Run this on the **machine with After Effects installed** (Mac or Windows).

---

## Quick Start

### Option A: Node.js MCP Server (Recommended)

```bash
cd production/adobe/ae_mcp_server
npm install
node index.js
```

**On Mac:** After Effects launches and runs the script.
**On Windows:** Same — AE runs and executes scripts.

### Option B: Python HTTP Server (Remote Bridge)

If you want WSL to connect to a **remote** AE machine over HTTP:

```bash
cd production/adobe/ae_mcp_server
python server.py --port 8765
```

Then in WSL, use `AEBridge(host="<AE-machine-ip>", port=8765)`.

---

## Architecture

```
┌─────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│  WSL (Claude)   │ ──► │  AE MCP Server       │ ──► │ After Effects   │
│  AEBridge       │     │  (Node.js / Python)  │     │  (AE DOM/JSX)   │
│  remote calls   │     │  on AE machine      │     │                 │
└─────────────────┘     └─────────────────────┘     └─────────────────┘
```

---

## Tools Exposed

| Tool | Description |
|------|-------------|
| `create_karaoke_captions` | Word-by-word animation: scale 80→100%, drop-in position, opacity 0→100, ease-out. Yellow highlights for emphasis words. |
| `apply_linear_wipe` | Linear wipe transition between two clips. Direction: left/right/top/bottom. |
| `apply_color_grade` | Lumetri color grade. Presets: cinematic, bright, vibrant, muted. |
| `create_composition` | New 9:16 composition at 1080x1920, 30fps. |
| `import_video` | Import video file into AE project. |
| `render_composition` | Render to H.264 MP4, 1080x1920, 30fps. |

---

## Example: Create Karaoke Captions

```python
# From WSL (remote)
from production.adobe.ae_bridge import AEBridge

bridge = AEBridge(host="192.168.1.100", port=8765)
result = bridge.create_karaoke_captions([
    {"text": "SICK", "start": 0.0, "end": 2.0, "highlight": False},
    {"text": "WAIT", "start": 4.5, "end": 7.0, "highlight": True},
    {"text": "FOR", "start": 4.5, "end": 7.0, "highlight": False},
    {"text": "IT", "start": 4.5, "end": 7.0, "highlight": False},
])
print(result.message)  # → "Karaoke captions created: 4 words across 4 layers"
```

---

## Requirements

- **After Effects** 2020 or later
- **Node.js** 18+ (for MCP server)
- **Python 3.12+** (for HTTP server)
- AE must be running when executing scripts
- Bangers font installed on AE machine (`~/.local/share/fonts/Bangers-Regular.ttf`)

---

## Troubleshooting

### "Adobe After Effects 2024 not found"
Set your AE version manually in `index.js` or `server.py`:
```javascript
// In index.js, change getAEVersion() return
return "2023"; // your version
```

### Scripts not executing
On macOS, make sure AE is installed in `/Applications/Adobe After Effects <version>/`.

### Remote connection refused
Check firewall: `python server.py --port 8765` needs port 8765 open on the AE machine.
