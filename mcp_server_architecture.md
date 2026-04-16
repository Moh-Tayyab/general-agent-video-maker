# MCP Server Architecture: Video Automation Bridge

## 1. Overview
The Video Automation Bridge is a Python-based MCP server that acts as the translation layer between the Orchestrator Agent's high-level intents (e.g., "upscale this video") and the low-level software execution (CLI commands, XML project manipulation, or Python scripting APIs).

## 2. Technical Stack
- **Language**: Python 3.12+
- **Protocol**: Model Context Protocol (MCP)
- **Communication**: stdio (Standard Input/Output)
- **Execution Methods**:
    - **Adobe Premiere/AE**: ExtendScript (via `.jsx` files) and XML (`.prproj` / `.aep` manipulation).
    - **Topaz AI**: CLI parameters (where available) or automation of the Topaz AI executable.
    - **OS Level**: `subprocess` for file movement and shell execution.

## 3. Component Diagram
`Orchestrator` $\rightarrow$ `MCP Server` $\rightarrow$ `Skill Dispatcher` $\rightarrow$ `Software-Specific Wrapper` $\rightarrow$ `Local Software`

### 3.1 Software-Specific Wrappers
- **PremiereWrapper**: Handles `.jsx` script injection for rough cuts and audio mixing.
- **TopazWrapper**: Manages profiles and triggers the upscale process.
- **AEWrapper**: Generates SRT overlays and handles the render queue.

## 4. API Endpoints (MCP Tools)
The server will expose the following tools to Claude:
- `run_premiere_skill(skill_id, params)`: Executes a Premiere-specific task.
- `run_topaz_skill(skill_id, params)`: Executes a Topaz-specific task.
- `run_ae_skill(skill_id, params)`: Executes an After Effects-specific task.
- `validate_artifact(file_path, check_type)`: Verifies if the output file meets the Constitution's quality gates.
