#!/usr/bin/env python3
"""
AE_MCP_HTTP_Server.py

HTTP server that wraps After Effects ExtendScript calls.
Run this on the machine with After Effects installed.

Usage:
  python AE_MCP_HTTP_Server.py [--port 8765] [--platform mac|win]

Then WSL agents connect via:
  bridge = AEBridge(host="localhost", port=8765)  # same machine
  bridge = AEBridge(host="192.168.1.x", port=8765)  # remote machine

Tools exposed:
  - POST /create_karaoke_captions
  - POST /apply_linear_wipe
  - POST /apply_color_grade
  - POST /create_composition
  - POST /import_video
  - POST /render_composition
"""

import json
import subprocess
import os
import sys
import argparse
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AE_MCP] %(levelname)s %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("AE_MCP")


# ─── Platform Detection ─────────────────────────────────────────────────────

def detect_platform():
    if sys.platform == "darwin":
        return "mac"
    elif sys.platform in ("win32", "cygwin"):
        return "win"
    else:
        return "mac"  # default


def get_ae_path():
    """Find After Effects executable."""
    plat = detect_platform()
    if plat == "mac":
        versions = ["2024", "2023", "2022", "2021", "2020"]
        for v in versions:
            path = f"/Applications/Adobe After Effects {v}/Adobe After Effects {v}.app"
            if os.path.exists(path):
                return v
    else:  # win
        for v in ["2024", "2023", "2022", "2021", "2020"]:
            base = os.environ.get("ProgramFiles", "C:\\Program Files")
            path = os.path.join(
                base, f"Adobe\\Adobe After Effects {v}\\Support Files\\AfterFX.exe"
            )
            if os.path.exists(path):
                return v
    return "2024"


# ─── ExtendScript Runner ────────────────────────────────────────────────────

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def run_jsx(jsx_code: str, ae_version: str = None) -> dict:
    """Execute ExtendScript code on After Effects."""
    if not ae_version:
        ae_version = get_ae_path()

    plat = detect_platform()

    # Write script to temp file
    script_file = os.path.join(SCRIPTS_DIR, "_temp_execute.jsx")
    with open(script_file, "w", encoding="utf-8") as f:
        f.write("#target aftereffects\n")
        f.write(jsx_code)

    try:
        if plat == "mac":
            script_path = os.path.abspath(script_file)
            cmd = [
                "osascript",
                "-e",
                f'tell application "Adobe After Effects {ae_version}"',
                "-e",
                f'DoScriptFile (POSIX file "{script_path}")',
                "-e",
                "end tell",
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=180, check=True
            )
            return {"success": True, "output": result.stdout.strip()}

        else:  # win
            ae_exe = os.environ.get(
                "ProgramFiles",
                "C:\\Program Files",
            ) + f"\\Adobe\\Adobe After Effects {ae_version}\\Support Files\\AfterFX.exe"
            cmd = f'"{ae_exe}" -r "{os.path.abspath(script_file)}"'
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=180, check=True
            )
            return {"success": True, "output": result.stdout.strip()}

    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr or str(e)}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout (>3min)"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if os.path.exists(script_file):
            os.remove(script_file)


# ─── AE Operations ─────────────────────────────────────────────────────────

def op_create_karaoke(captions: list, font_size: int = 96, font_name: str = "Bangers", composition: str = "MavenEdit"):
    """Create word-by-word karaoke animation."""
    jsx = f"""
    var comp = null;
    for (var i = 1; i <= app.project.numItems; i++) {{
        if (app.project.item(i).name === "{composition}" && app.project.item(i) instanceof CompItem) {{
            comp = app.project.item(i);
            break;
        }}
    }}
    if (!comp) {{ throw new Error("Composition '{composition}' not found"); }}

    var fontSize = {font_size};
    var fontName = "{font_name}";
    var fontColor = [1.0, 1.0, 1.0, 1.0];
    var highlightColor = [1.0, 1.0, 0.0, 1.0];
    var strokeColor = [0.0, 0.0, 0.0, 1.0];
    var baselineY = comp.height * 0.75;
    var startScale = 80;
    var timingOffset = 0.05;
    var captions = {json.dumps(captions)};

    for (var i = 0; i < captions.length; i++) {{
        var cap = captions[i];
        var isHighlight = !!cap.highlight;
        var wordLayer = comp.layers.addText();
        wordLayer.name = "W_" + i + "_" + cap.text.replace(/\\s+/g, "_");

        var textProp = wordLayer.property("Source Text");
        var td = new TextDocument(cap.text);
        td.fontSize = fontSize;
        td.font = fontName;
        td.fillColor = isHighlight ? highlightColor : fontColor;
        td.strokeColor = strokeColor;
        td.strokeWidth = 0.06;
        td.strokeFill = true;
        td.justify = TextJustification.CENTER;
        textProp.setValueAtTime(0, td);

        var wordWidth = textProp.value.sourceRect.width;
        var wordCenterX = comp.width / 2 - wordWidth / 2;
        var wordStartX = wordCenterX;
        var wordStartY = baselineY + 20;
        var wordEndY = baselineY;

        // Position: drop from above
        wordLayer.position.setValueAtTime(cap.start - timingOffset, [wordStartX, wordStartY]);
        wordLayer.position.setValueAtTime(cap.start, [wordCenterX, wordEndY]);
        wordLayer.position.setValueAtTime(cap.start, [wordCenterX, wordEndY]);

        // Scale: 80 → 100
        wordLayer.scale.setValueAtTime(cap.start - timingOffset, [startScale, startScale, 100]);
        wordLayer.scale.setValueAtTime(cap.start, [100, 100, 100]);

        // Opacity: 0 → 100
        wordLayer.opacity.setValueAtTime(cap.start - timingOffset, 0);
        wordLayer.opacity.setValueAtTime(cap.start, 100);
    }}
    "ok";
    """
    return run_jsx(jsx)


def op_linear_wipe(clipA: str, clipB: str, direction: str = "left", duration: float = 1.0, softness: float = 0.1):
    """Apply linear wipe transition between two clips."""
    jsx = f"""
    var proj = app.project;
    var clipA = proj.importFile(new File("{clipA.replace('\\\\', '\\\\\\\\')}"));
    var clipB = proj.importFile(new File("{clipB.replace('\\\\', '\\\\\\\\')}"));
    var comp = proj.items.addCompItem("WipeComp", 1080, 1920, 1, {duration}, 30);

    var layerA = comp.layers.add(clipA);
    var layerB = comp.layers.add(clipB);
    layerB.moveAfter(layerA);

    var transitionStart = layerA.source.duration - {duration};
    var wipeEffect = layerB.property("Effects").addProperty("ADBE Wipe");
    wipeEffect.property("Transition Completion").setValueAtTime(transitionStart, 0);
    wipeEffect.property("Transition Completion").setValueAtTime(transitionStart + {duration}, 100);
    wipeEffect.property("Edge Feather").setValueAtTime(transitionStart, {softness * 5});
    "ok";
    """
    return run_jsx(jsx)


def op_color_grade(composition: str = "MavenEdit", preset: str = "cinematic", intensity: float = 0.8):
    """Apply Lumetri color grading."""
    preset_settings = {
        "cinematic": {"blacks": -5, "whites": 5, "saturation": -5},
        "bright": {"blacks": 20, "whites": 10, "saturation": 5},
        "vibrant": {"saturation": 20, "hi-lights": 5},
        "muted": {"saturation": -15, "contrast": 10},
    }
    settings = preset_settings.get(preset, preset_settings["cinematic"])

    jsx = f"""
    var comp = null;
    for (var i = 1; i <= app.project.numItems; i++) {{
        if (app.project.item(i).name === "{composition}" && app.project.item(i) instanceof CompItem) {{
            comp = app.project.item(i);
            break;
        }}
    }}
    if (!comp) {{ throw new Error("Composition '{composition}' not found"); }}

    for (var j = 1; j <= comp.numLayers; j++) {{
        var lum = comp.layer(j).property("Effects").addProperty("ADBE Lumetri");
        for (var k in {json.dumps(settings)}).entries()) {{
            lum.property(k[0]).setValueAtTime(0, k[1]);
        }}
        lum.property("Intensity").setValueAtTime(0, {intensity * 100});
    }}
    "ok";
    """
    return run_jsx(jsx)


def op_create_composition(name: str = "MavenEdit", width: int = 1080, height: int = 1920, fps: int = 30, duration: float = 60.0):
    """Create new AE composition."""
    jsx = f"""
    var comp = app.project.items.addCompItem("{name}", {width}, {height}, 1, {duration}, {fps});
    comp.bgColor = [0, 0, 0];
    JSON.stringify({{ name: comp.name, duration: comp.duration }});
    """
    return run_jsx(jsx)


def op_import_video(videoPath: str, projectName: str = "source_video"):
    """Import video file into AE."""
    jsx = f"""
    var footageFile = new File("{videoPath.replace('\\\\', '\\\\\\\\')}");
    var imported = app.project.importFile(footageFile);
    imported.name = "{projectName}";
    JSON.stringify({{ name: imported.name }});
    """
    return run_jsx(jsx)


def op_render(composition: str, outputPath: str, quality: str = "high"):
    quality_map = {"high": 100, "medium": 70, "draft": 30}
    q = quality_map.get(quality, 100)
    jsx = f"""
    var comp = null;
    for (var i = 1; i <= app.project.numItems; i++) {{
        if (app.project.item(i).name === "{composition}" && app.project.item(i) instanceof CompItem) {{
            comp = app.project.item(i);
            break;
        }}
    }}
    if (!comp) {{ throw new Error("Composition '{composition}' not found"); }}
    var om = comp.outputModule(1);
    om.setSetting("Output File", "{outputPath.replace('\\\\', '\\\\\\\\')}");
    om.saveAsFile(new File("{outputPath.replace('\\\\', '\\\\\\\\')}"));
    "ok";
    """
    return run_jsx(jsx)


# ─── HTTP Server ────────────────────────────────────────────────────────────

class AEHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(format % args)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Read body
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        data = json.loads(body) if body else {}

        try:
            if path == "/create_karaoke_captions":
                result = op_create_karaoke(
                    data.get("captions", []),
                    data.get("fontSize", 96),
                    data.get("fontName", "Bangers"),
                    data.get("compositionName", "MavenEdit")
                )
            elif path == "/apply_linear_wipe":
                result = op_linear_wipe(
                    data.get("clipA_path"),
                    data.get("clipB_path"),
                    data.get("direction", "left"),
                    data.get("duration", 1.0),
                    data.get("softness", 0.1)
                )
            elif path == "/apply_color_grade":
                result = op_color_grade(
                    data.get("compositionName", "MavenEdit"),
                    data.get("preset", "cinematic"),
                    data.get("intensity", 0.8)
                )
            elif path == "/create_composition":
                result = op_create_composition(
                    data.get("name", "MavenEdit"),
                    data.get("width", 1080),
                    data.get("height", 1920),
                    data.get("fps", 30),
                    data.get("duration", 60.0)
                )
            elif path == "/import_video":
                result = op_import_video(
                    data.get("videoPath"),
                    data.get("projectName", "source_video")
                )
            elif path == "/render_composition":
                result = op_render(
                    data.get("compositionName"),
                    data.get("outputPath"),
                    data.get("quality", "high")
                )
            else:
                result = {"success": False, "error": f"Unknown endpoint: {path}"}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

        except Exception as e:
            logger.error(f"Error: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"AE MCP Server OK")
        else:
            self.send_response(404)
            self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="AE MCP HTTP Server")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--platform", choices=["mac", "win"], help="Override platform detection")
    args = parser.parse_args()

    logger.info(f"Starting AE MCP server on {args.host}:{args.port}")
    logger.info(f"Platform: {args.platform or detect_platform()}")
    logger.info(f"Scripts dir: {SCRIPTS_DIR}")

    server = HTTPServer((args.host, args.port), AEHandler)
    logger.info(f"AE MCP server ready at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()