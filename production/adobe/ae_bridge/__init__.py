"""
AE Bridge — Python interface to the Adobe After Effects MCP server.

Two usage modes:

  1. LOCAL (same machine as AE): add MCP server to settings.json
     → agent uses it directly via Skill tool

  2. REMOTE (AE on Windows/Mac, agent on WSL):
     → use AEBridge.remote_* methods which make HTTP calls to the remote MCP server

Usage (remote mode):
    bridge = AEBridge(host="192.168.1.100", port=8765)
    result = bridge.create_karaoke_captions(captions)
    result = bridge.render_composition("MavenEdit", "/tmp/output.mp4")

Usage (local mode):
    import subprocess
    # Add to ~/.claude/settings.json:
    # "mcpServers": { "adobe-after-effects": { "command": "node", "args": ["AE_MCP_SERVER/index.js"] }}
    # Then agent uses it directly
"""
import subprocess
import json
import os
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

logger = logging.getLogger("AEBridge")


@dataclass
class Caption:
    text: str
    start: float
    end: float
    highlight: bool = False


@dataclass
class AEResult:
    success: bool
    message: str
    output: Optional[Dict[str, Any]] = None


class AEBridge:
    """
    Bridge to After Effects MCP server.
    Can run locally (same machine) or connect to remote via HTTP.
    """

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"

    # ─── Remote HTTP Calls (for when AE MCP runs on remote machine) ─────────

    def _call_remote(self, tool: str, arguments: Dict[str, Any]) -> AEResult:
        """Make HTTP call to remote MCP server."""
        import urllib.request
        import urllib.error

        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": arguments
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/call/{tool}",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read().decode("utf8"))
                return AEResult(
                    success=not data.get("isError", False),
                    message=data.get("content", [{}])[0].get("text", ""),
                    output=data
                )
        except urllib.error.URLError as e:
            return AEResult(False, f"Connection failed: {e}")

    # ─── Karaoke Captions ───────────────────────────────────────────────────

    def create_karaoke_captions(
        self,
        captions: List[Dict],
        font_size: int = 96,
        font_name: str = "Bangers",
        composition_name: str = "MavenEdit"
    ) -> AEResult:
        """
        Create word-by-word animated karaoke captions.
        Each caption: { text, start, end, highlight }

        Example:
            bridge.create_karaoke_captions([
                {"text": "SICK", "start": 0.0, "end": 2.0, "highlight": False},
                {"text": "WAIT", "start": 4.5, "end": 7.0, "highlight": True},
            ])
        """
        return self._call_remote("create_karaoke_captions", {
            "captions": captions,
            "fontSize": font_size,
            "fontName": font_name,
            "compositionName": composition_name
        })

    # ─── Linear Wipe Transition ────────────────────────────────────────────

    def apply_linear_wipe(
        self,
        clipA_path: str,
        clipB_path: str,
        direction: str = "left",
        duration: float = 1.0,
        softness: float = 0.1
    ) -> AEResult:
        """Apply a linear wipe transition between two clips."""
        return self._call_remote("apply_linear_wipe", {
            "clipA_path": clipA_path,
            "clipB_path": clipB_path,
            "direction": direction,
            "duration": duration,
            "softness": softness
        })

    # ─── Color Grading ─────────────────────────────────────────────────────

    def apply_color_grade(
        self,
        composition_name: str = "MavenEdit",
        preset: str = "cinematic",
        intensity: float = 0.8
    ) -> AEResult:
        """Apply Lumetri color grading. Presets: cinematic, bright, vibrant, muted."""
        return self._call_remote("apply_color_grade", {
            "compositionName": composition_name,
            "preset": preset,
            "intensity": intensity
        })

    # ─── Composition ───────────────────────────────────────────────────────

    def create_composition(
        self,
        name: str = "MavenEdit",
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        duration: float = 60.0
    ) -> AEResult:
        """Create a new AE composition (defaults to 9:16 Shorts format)."""
        return self._call_remote("create_composition", {
            "name": name,
            "width": width,
            "height": height,
            "fps": fps,
            "duration": duration
        })

    def import_video(
        self,
        video_path: str,
        project_name: str = "MavenEdit"
    ) -> AEResult:
        """Import a video file into AE project."""
        return self._call_remote("import_video", {
            "videoPath": video_path,
            "projectName": project_name
        })

    # ─── Render ─────────────────────────────────────────────────────────────

    def render_composition(
        self,
        composition_name: str,
        output_path: str,
        quality: str = "high"
    ) -> AEResult:
        """
        Render composition to MP4.
        Output: 1080x1920, 30fps, H.264, AAC.
        """
        return self._call_remote("render_composition", {
            "compositionName": composition_name,
            "outputPath": output_path,
            "quality": quality
        })

    # ─── Local Execution (macOS) ───────────────────────────────────────────

    def run_local_script(self, script_name: str, params: Dict[str, Any] = None) -> AEResult:
        """Run an AE script locally via osascript (macOS only)."""
        if not params:
            params = {}

        script_path = f"/home/muhammad_tayyab/bootlogix/production/adobe/ae_mcp_server/ae_scripts/{script_name}"

        cmd = [
            "osascript",
            "-e",
            f'tell application "Adobe After Effects 2024"',
            "-e", f'DoScriptFile (POSIX file "{script_path}")',
            "-e", "end tell"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return AEResult(True, "Script executed", {})
            return AEResult(False, result.stderr)
        except subprocess.TimeoutExpired:
            return AEResult(False, "Script timed out")
        except Exception as e:
            return AEResult(False, str(e))