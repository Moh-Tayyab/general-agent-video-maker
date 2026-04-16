# Final Deployment & Execution Guide: YouTube Automation Pipeline

This guide details how to move the agentic system from the "Simulation" phase to "Production" execution on your local machine.

## 1. Environment Prerequisites
Ensure the following are installed and accessible in your system PATH:
- **Python 3.12+**
- **Adobe Premiere Pro 2024**
- **Adobe After Effects 2024**
- **Topaz Video AI**
- **FFmpeg** (Required for the Validation Engine's `ffprobe` checks)

## 2. Configure Claude Desktop (The MCP Connection)
To allow Claude to control this pipeline, you must register the bridge in your Claude Desktop config.

1. Open your `claude_desktop_config.json`:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add the following block under `mcpServers`:
```json
{
  "mcpServers": {
    "video-automation-bridge": {
      "command": "python",
      "args": [
        "-u",
        "/home/muhammad_tayyab/bootlogix/mcp_bridge/server.py"
      ],
      "env": {
        "PREMIERE_PATH": "C:\\Program Files\\Adobe\\Adobe Premiere Pro 2024\\Adobe Premiere Pro.exe",
        "TOPAZ_PATH": "C:\\Program Files\\Topaz Labs LLC\\Topaz Video AI\\Topaz Video AI.exe",
        "AE_PATH": "C:\\Program Files\\Adobe\\Adobe After Effects 2024\\AfterFX.exe",
        "PROJECT_ROOT": "/home/muhammad_tayyab/bootlogix/projects"
      }
    }
  }
}
```

## 3. Executing a Project
Once configured, you can trigger the pipeline using the Project Runner CLI or by asking Claude:

**Via Claude Desktop:**
> "Start the video automation pipeline for project 'Video_01'. Use the established constitution and workflow spec."

**Via CLI (Manual):**
```bash
python3 /home/muhammad_tayyab/bootlogix/mcp_bridge/run_project.py --id Video_01
```

## 4. Monitoring & Debugging
The system maintains detailed logs of every agent action:
- **Orchestrator Log**: `/home/muhammad_tayyab/bootlogix/mcp_bridge/orchestrator.log`
- **Agent Log**: `/home/muhammad_tayyab/bootlogix/mcp_bridge/agent_pipeline.log`

If a project fails at a **Quality Gate**, check the logs to see exactly which `ValidationEngine` check failed (e.g., resolution mismatch or missing artifact).
