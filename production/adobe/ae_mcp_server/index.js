/**
 * After Effects MCP Server
 *
 * Exposes After Effects operations as MCP tools for use by Claude Code agents.
 * Connects to After Effects via ExtendScript execution.
 *
 * Usage:
 *   node index.js [--platform=mac|win]
 *
 * Tools exposed:
 *   - create_karaoke_captions   — word-by-word animated captions
 *   - apply_linear_wipe         — wipe transition between two clips
 *   - apply_color_grade         — Lumetri color grading
 *   - create_text_layer         — styled text overlay
 *   - render_composition        — export to H.264 MP4
 *   - import_video              — import video file into project
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { readFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { execSync, spawn } from "child_process";
import { platform } from "process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const AE_SCRIPTS_DIR = join(__dirname, "ae_scripts");

// ─── Platform Detection ────────────────────────────────────────────────────

const args = process.argv.slice(2);
const isMac = args.includes("--platform=mac") || platform === "darwin";
const isWin = args.includes("--platform=win") || (platform === "win32" && !isMac);

// ─── ExtendScript Executor ───────────────────────────────────────────────────

function runExtendScript(scriptContent) {
  const scriptPath = join(AE_SCRIPTS_DIR, "temp_execute.jsx");

  // Write script to temp file (so it can include other files)
  const fullScript = scriptContent;
  require("fs").writeFileSync(scriptPath, fullScript, "utf8");

  try {
    if (isMac) {
      // macOS: use osascript to run .jsx via Adobe ExtendScript Toolkit
      const cmd = [
        "osascript",
        "-e",
        `tell application "Adobe After Effects ${getAEVersion()}"`,
        `-e "DoScriptFile (POSIX file "${scriptPath}")"`,
        "-e \"end tell\""
      ];
      const result = execSync(cmd.join(" "), { encoding: "utf8", timeout: 120000 });
      return { success: true, output: result };
    } else if (isWin) {
      // Windows: use afterfx.exe with -r flag or COM
      const aePath = getAEPath();
      const cmd = `"${aePath}" -r "${scriptPath}"`;
      const result = execSync(cmd, { encoding: "utf8", timeout: 120000, shell: true });
      return { success: true, output: result };
    }
  } catch (err) {
    return { success: false, error: err.message, stderr: err.stderr || "" };
  }
}

function getAEVersion() {
  // Try common AE versions
  const versions = ["2024", "2023", "2022", "2021", "2020"];
  for (const v of versions) {
    try {
      const path = isMac
        ? `/Applications/Adobe After Effects ${v}/Adobe After Effects ${v}.app`
        : `C:\\Program Files\\Adobe\\Adobe After Effects ${v}\\Support Files\\AfterFX.exe`;
      if (existsSync(path)) return v;
    } catch (_) {}
  }
  return "2024";
}

function getAEPath() {
  const v = getAEVersion();
  return isMac
    ? `/Applications/Adobe After Effects ${v}/Adobe After Effects ${v}.app`
    : `C:\\Program Files\\Adobe\\Adobe After Effects ${v}\\Support Files\\AfterFX.exe`;
}

// ─── Load AE Scripts ────────────────────────────────────────────────────────

function loadScript(filename) {
  const path = join(AE_SCRIPTS_DIR, filename);
  if (!existsSync(path)) {
    throw new Error(`Script not found: ${path}`);
  }
  return readFileSync(path, "utf8");
}

// ─── MCP Server ─────────────────────────────────────────────────────────────

const server = new Server(
  {
    name: "adobe-after-effects",
    version: "1.0.0"
  },
  {
    tools: {
      [ListToolsRequestSchema]: () => ({
        tools: [
          {
            name: "create_karaoke_captions",
            description:
              "Create professional word-by-word karaoke captions in After Effects. " +
              "Each word animates with: scale pop (80→100%), position drop-in from above, " +
              "and opacity fade-in. Words are centered in the lower third. " +
              "Yellow highlights with black stroke. Perfect for Maven-Edit style videos.",
            inputSchema: {
              type: "object",
              properties: {
                captions: {
                  type: "array",
                  description: "Array of caption objects with text, start time (seconds), end time, and highlight flag",
                  items: {
                    type: "object",
                    properties: {
                      text: { type: "string", description: "The word or phrase" },
                      start: { type: "number", description: "Start time in seconds" },
                      end: { type: "number", description: "End time in seconds" },
                      highlight: {
                        type: "boolean",
                        description: "Whether this word uses yellow highlight color"
                      }
                    },
                    required: ["text", "start", "end"]
                  }
                },
                fontSize: { type: "number", default: 96, description: "Caption font size in pixels" },
                fontName: { type: "string", default: "Bangers", description: "Font family name" },
                compositionName: { type: "string", default: "MavenEdit", description: "AE composition name" }
              },
              required: ["captions"]
            }
          },
          {
            name: "apply_linear_wipe",
            description:
              "Apply a linear wipe transition between two video clips. " +
              "Direction: left (wipes from right), right (wipes from left), top, bottom. " +
              "Includes edge softness control.",
            inputSchema: {
              type: "object",
              properties: {
                clipA_path: { type: "string", description: "Path to first video clip" },
                clipB_path: { type: "string", description: "Path to second video clip" },
                direction: {
                  type: "string",
                  enum: ["left", "right", "top", "bottom"],
                  default: "left",
                  description: "Wipe direction"
                },
                duration: {
                  type: "number",
                  default: 1.0,
                  description: "Transition duration in seconds"
                },
                softness: {
                  type: "number",
                  default: 0.1,
                  description: "Edge softness (0-1)"
                }
              },
              required: ["clipA_path", "clipB_path"]
            }
          },
          {
            name: "apply_color_grade",
            description:
              "Apply Lumetri Color grading to a composition. " +
              "Presets: 'cinematic' (contrast +8, sat -5), 'bright', 'vibrant', 'muted'. " +
              "Maven-Edit uses 'cinematic'.",
            inputSchema: {
              type: "object",
              properties: {
                compositionName: { type: "string", description: "Target composition name" },
                preset: {
                  type: "string",
                  enum: ["cinematic", "bright", "vibrant", "muted"],
                  default: "cinematic"
                },
                intensity: {
                  type: "number",
                  default: 0.8,
                  description: "Effect intensity (0-1)"
                }
              },
              required: ["compositionName"]
            }
          },
          {
            name: "render_composition",
            description:
              "Render an After Effects composition to H.264 MP4. " +
              "Output: 1080x1920 (9:16), 30fps, H.264, AAC audio.",
            inputSchema: {
              type: "object",
              properties: {
                compositionName: { type: "string", description: "Composition to render" },
                outputPath: {
                  type: "string",
                  description: "Full output file path (must end in .mp4)"
                },
                codec: { type: "string", default: "H.264", description: "Video codec" },
                quality: {
                  type: "string",
                  enum: ["draft", "medium", "high"],
                  default: "high"
                }
              },
              required: ["compositionName", "outputPath"]
            }
          },
          {
            name: "import_video",
            description:
              "Import a video file into the After Effects project. " +
              "Returns the import name for use in subsequent calls.",
            inputSchema: {
              type: "object",
              properties: {
                videoPath: { type: "string", description: "Full path to video file" },
                projectName: { type: "string", default: "MavenEdit" }
              },
              required: ["videoPath"]
            }
          },
          {
            name: "create_composition",
            description:
              "Create a new After Effects composition. " +
              "Defaults to 1080x1920 (9:16 vertical) at 30fps — perfect for Shorts.",
            inputSchema: {
              type: "object",
              properties: {
                name: { type: "string", default: "MavenEdit" },
                width: { type: "number", default: 1080 },
                height: { type: "number", default: 1920 },
                fps: { type: "number", default: 30 },
                duration: { type: "number", default: 60, description: "Duration in seconds" }
              },
              required: ["name"]
            }
          }
        ]
      })
    }
  }
);

// ─── Tool Handlers ──────────────────────────────────────────────────────────

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "create_karaoke_captions": {
        const { captions, fontSize, fontName, compositionName } = args;

        const script = `
          #target aftereffects
          ${loadScript("karaoke_animation.jsx")}
          var proj = app.project;
          var comp = null;
          for (var i = 1; i <= proj.numItems; i++) {
            if (proj.item(i).name === "${compositionName || "MavenEdit"}" && proj.item(i) instanceof CompItem) {
              comp = proj.item(i);
              break;
            }
          }
          if (!comp) throw new Error("Composition '${compositionName || "MavenEdit"}' not found");
          var result = ae_karaoke_create_simple(proj, comp, ${JSON.stringify(captions)});
          JSON.stringify({ status: "ok", layers: result });
        `;

        const result = runExtendScript(script);
        if (!result.success) throw new Error(result.error);

        return {
          content: [
            {
              type: "text",
              text: `Karaoke captions created: ${captions.length} words across ${captions.length} layers`
            }
          ]
        };
      }

      case "apply_linear_wipe": {
        const { clipA_path, clipB_path, direction, duration, softness } = args;

        const script = `
          #target aftereffects
          ${loadScript("transitions.jsx")}
          var proj = app.project;
          var clipA = proj.importFile(new File("${clipA_path.replace(/\\/g, "\\\\")}"));
          var clipB = proj.importFile(new File("${clipB_path.replace(/\\/g, "\\\\")}"));
          var comp = proj.items.addCompItem("WipeComp", 1080, 1920, 1, ${duration || 1.0}, 30);
          ae_linear_wipe(clipA, clipB, comp, {
            direction: "${direction || "left"}",
            duration: ${duration || 1.0},
            softness: ${softness || 0.1}
          });
          "ok";
        `;

        const result = runExtendScript(script);
        if (!result.success) throw new Error(result.error);

        return {
          content: [{ type: "text", text: `Linear wipe applied (${direction}, ${duration}s)` }]
        };
      }

      case "apply_color_grade": {
        const { compositionName, preset, intensity } = args;

        const script = `
          #target aftereffects
          ${loadScript("transitions.jsx")}
          var proj = app.project;
          var comp = null;
          for (var i = 1; i <= proj.numItems; i++) {
            if (proj.item(i).name === "${compositionName}" && proj.item(i) instanceof CompItem) {
              comp = proj.item(i);
              break;
            }
          }
          if (!comp) throw new Error("Composition not found: ${compositionName}");
          for (var j = 1; j <= comp.numLayers; j++) {
            ae_color_grade_lumetri(comp.layer(j), {
              preset: "${preset || "cinematic"}",
              intensity: ${intensity || 0.8}
            });
          }
          "ok";
        `;

        const result = runExtendScript(script);
        if (!result.success) throw new Error(result.error);

        return {
          content: [{ type: "text", text: `Color grade applied: ${preset || "cinematic"}` }]
        };
      }

      case "render_composition": {
        const { compositionName, outputPath, quality } = args;

        const script = `
          #target aftereffects
          var proj = app.project;
          var comp = null;
          for (var i = 1; i <= proj.numItems; i++) {
            if (proj.item(i).name === "${compositionName}" && proj.item(i) instanceof CompItem) {
              comp = proj.item(i);
              break;
            }
          }
          if (!comp) throw new Error("Composition not found: ${compositionName}");
          var outputModule = comp.outputModule(1);
          var settings = outputModule.user guides ? outputModule.user guides : null;
          outputModule.setSetting("Output File", "${outputPath.replace(/\\/g, "\\\\")}");
          outputModule.setSetting("Video Codec", "H.264");
          outputModule.setSetting("Quality", "${quality === "high" ? 100 : quality === "medium" ? 70 : 30}");
          comp.saveFrameToJPEG(comp.time, new File("${outputPath.replace(/\\/g, "\\\\").replace(".mp4", "_thumb.jpg")}"));
          outputModule.saveAsFile(new File("${outputPath.replace(/\\/g, "\\\\")}"));
          "ok";
        `;

        const result = runExtendScript(script);
        if (!result.success) throw new Error(result.error);

        return {
          content: [
            { type: "text", text: `Rendered: ${outputPath}` }
          ]
        };
      }

      case "import_video": {
        const { videoPath, projectName } = args;

        const script = `
          #target aftereffects
          var proj = app.project;
          var footageFile = new File("${videoPath.replace(/\\/g, "\\\\")}");
          var imported = proj.importFile(footageFile);
          imported.name = "${projectName || "source_video"}";
          JSON.stringify({ importName: imported.name, type: imported.type });
        `;

        const result = runExtendScript(script);
        if (!result.success) throw new Error(result.error);

        return {
          content: [
            { type: "text", text: `Imported: ${videoPath}` }
          ]
        };
      }

      case "create_composition": {
        const { name, width, height, fps, duration } = args;

        const script = `
          #target aftereffects
          var proj = app.project;
          var comp = proj.items.addCompItem(
            "${name}",
            ${width || 1080},
            ${height || 1920},
            1,
            ${duration || 60},
            ${fps || 30}
          );
          comp.bgColor = [0, 0, 0];
          JSON.stringify({ name: comp.name, duration: comp.duration, width: comp.width, height: comp.height });
        `;

        const result = runExtendScript(script);
        if (!result.success) throw new Error(result.error);

        return {
          content: [
            { type: "text", text: `Created composition: ${name} (${width}x${height}, ${fps}fps)` }
          ]
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (err) {
    return {
      content: [{ type: "text", text: `Error: ${err.message}` }],
      isError: true
    };
  }
});

// ─── Start Server ────────────────────────────────────────────────────────────

const transport = new StdioServerTransport();
server.connect(transport);

console.error("Adobe After Effects MCP server started");
process.stderr.write("Adobe After Effects MCP server running\\n");