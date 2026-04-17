# MCP Server Architecture: Video Automation Bridge

## 1. Overview
The Video Automation Bridge is a Python-based MCP server that acts as the translation layer between the Orchestrator Agent's high-level intents (e.g., "upscale this video") and the low-level software execution. It also manages the **SSD Pipeline State** (Search -> Script -> Design -> Generate) via a persistent project manifest system.

## 2. Technical Stack
- **Language**: Python 3.12+
- **Protocol**: Model Context Protocol (MCP)
- **Communication**: stdio (Standard Input/Output)
- **State Management**: JSON-based `ProjectManifest` tracked via `ManifestManager`.

## 3. Component Diagram
`Orchestrator` $\leftrightarrow$ `MCP Server` $\leftrightarrow$ `ManifestTool` $\leftrightarrow$ `Disk Storage`
                          $\downarrow$
                  `Skill Dispatcher` $\rightarrow$ `Bridges` $\rightarrow$ `Local Software / CLI`

### 3.1 Core Components
- **ManifestTool**: High-level interface for project initialization, phase transitions, and artifact recording.
- **Bridges**: Specialist wrappers for YouTube, Captions (ElevenLabs/ASS), Render (FFmpeg), and Topaz AI.
- **AdobeBridge**: Handles JSX generation and delivery to Adobe software via drop-zones.

## 4. API Endpoints (MCP Tools)

### 4.1 Project Management (SSD Pipeline)
- `project_init(project_id, metadata)`: Start a new production project.
- `project_get_state(project_id)`: Get current phase, status, and artifacts.
- `project_record_artifact(project_id, phase, key, content)`: Record a file or data artifact.
- `project_transition_phase(project_id, target_phase)`: Move to the next SSD phase.
- `project_complete_phase(project_id)`: Mark the current phase as completed.

### 4.2 Production Tools
- `youtube_upload(...)`: Direct upload to YouTube via API.
- `caption_transcribe(...)`: STT and timing extraction.
- `caption_generate_ass(...)`: Maven-style karaoke caption generation.
- `render_burn_captions(...)`: FFmpeg-based caption burn-in.
- `topaz_upscale(...)`: AI resolution enhancement.
- `quality_validate(...)`: Automated quality gate checks.
