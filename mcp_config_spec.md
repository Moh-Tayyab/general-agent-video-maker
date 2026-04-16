# MCP Config Specification: claude_desktop_config.json

To integrate the Video Automation Bridge with the Claude Desktop App, the following configuration must be added to the `mcpServers` section of the `claude_desktop_config.json` file.

## 1. Config Path
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

## 2. Configuration Block
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

## 3. Implementation Details
- **`-u` flag**: Ensures unbuffered output, which is critical for the MCP stdio communication to avoid hangs.
- **Environment Variables**: Instead of hardcoding paths in the Python script, we use environment variables to allow for easy updates across different machines or software versions.
- **Security**: The server runs as a local process with the user's permissions, allowing it to interact with the local filesystem and installed Adobe/Topaz software.
