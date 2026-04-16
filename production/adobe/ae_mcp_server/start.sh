#!/bin/bash
# start_ae_mcp.sh — Start AE MCP server on the machine with After Effects

cd "$(dirname "$0")"

PLATFORM=$(uname)

if [[ "$PLATFORM" == "Darwin" ]]; then
    echo "Starting AE MCP server (Node.js) on macOS..."
    npm install 2>/dev/null
    node index.js
elif [[ "$PLATFORM" == *"MINGW"* || "$PLATFORM" == *"CYGWIN"* || -d "/mnt/c" ]]; then
    echo "Starting AE MCP server (Python HTTP) on Windows..."
    python server.py --port 8765 --platform win
else
    echo "Starting AE MCP server (Python HTTP) on Linux..."
    python server.py --port 8765 --platform mac
fi