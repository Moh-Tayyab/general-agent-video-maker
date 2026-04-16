# Bootlogix Video Constitution

> Authored: 2026-04-15
> Version: 1.0.0
> Type: Video production pipeline constitution
> Replaces: `video-automation-constitution.md`

---

## 1. Core Objective

Produce viral YouTube Shorts (9:16, 30-60s) via an autonomous SSD pipeline using Claude Code's native multi-agent team system.

**Pipeline phases:**
```
SEARCH → SCRIPT → DESIGN → GENERATE
```

---

## 2. Team Architecture

**Team:** `video-pipeline`

| Member | Type | Phase | Skills |
|--------|------|-------|--------|
| `orchestrator` | team-lead | Coordinator | — |
| `researcher` | general-purpose | SEARCH | `find-skills`, `mcp__youtube-shorts-transcript-extractor` |
| `scriptwriter` | general-purpose | SCRIPT | `copywriting`, `elevenlabs-tts` |
| `visual-designer` | general-purpose | DESIGN | `ai-video-generation` |
| `producer` | general-purpose | GENERATE | `remotion`, `remotion-best-practices`, `elevenlabs-tts`, `ai-video-generation` |

### Agent Prompts
Located in `agents/prompts/`:
- `researcher_agent.py` — `RESEARCHER_PROMPT`
- `scriptwriter_agent.py` — `SCRIPTWRITER_PROMPT`
- `visual_designer_agent.py` — `VISUAL_DESIGNER_PROMPT`
- `producer_agent.py` — `PRODUCER_PROMPT`
- `video-orchestrator.md` — orchestrator coordination guide

### Coordination Protocol
1. `TaskCreate` — one task per SSD phase
2. `Agent(team_name="video-pipeline", name="<agent>", taskId=N)` — spawn phase agent
3. `SendMessage(to="orchestrator")` — agents report completion
4. `TaskUpdate` — mark tasks in_progress / completed

---

## 3. Phase Specifications

### 3.1 SEARCH
**Agent:** `researcher`
**Skills:** `find-skills`, `mcp__youtube-shorts-transcript-extractor`

**Inputs:** Topic or keyword
**Outputs:**
- `topic`: Refined topic
- `source_urls`: Relevant source URLs
- `transcript`: Key transcript excerpts
- `hooks`: Potential viral hooks
- `story_beats`: Key moments to capture

**Quality gate:** Verify transcript accuracy; flag generic sources lacking viral potential.

### 3.2 SCRIPT
**Agent:** `scriptwriter`
**Skills:** `copywriting`, `elevenlabs-tts`

**Inputs:** Research artifact from SEARCH
**Outputs:**
- `script_md`: Full script in markdown
- `narration_text`: Clean narration text ready for TTS
- `estimated_duration`: Approximate video duration (seconds)

**Quality gate:** Hook must capture attention in first 2s; pacing 150-180 words/30s.

### 3.3 DESIGN
**Agent:** `visual-designer`
**Skills:** `ai-video-generation`

**Inputs:** Script artifact from SCRIPT
**Outputs:**
- `storyboard_json`: Array of scene objects with visual prompts
- `asset_list`: Required assets (footage, images)
- `style_guide`: Visual consistency guidelines
- `scene_timing`: Expected duration per scene

**Quality gate:** Each scene prompt specific enough for AI generation; style consistency across scenes.

### 3.4 GENERATE
**Agent:** `producer`
**Skills:** `elevenlabs-tts`, `ai-video-generation`, `remotion`, `remotion-best-practices`

**Inputs:** Design artifact from DESIGN
**Outputs:**
- `voiceover_wav`: Full voiceover audio file
- `footage_clips`: Array of generated video clip paths
- `remotion_project`: Remotion project folder
- `final_render`: Final rendered MP4
- `qa_report`: Quality assessment

**Quality gate:** 9:16 vertical format; 30-60s duration; audio-video sync; captions readable at 1080p.

---

## 4. Failure Recovery

- **Retry limit:** 3 automated retries per scene
- **Fallback:** Flag failing scene; continue with remaining scenes; report via `SendMessage`
- **QA cycle:** On persistent failure, reset artifact, provide targeted feedback, re-trigger generation

---

## 5. Artifact Naming

All artifacts: `ProjectID_Phase_Artifact_Version.ext`
Example: `MyProject_SCRIPT_v1.md`

---

## 6. Validation Tools

Quality gates use `production/validation/quality.py`:
- Duration check via `ffprobe`
- Resolution check via `ffprobe`
- File existence check

Adobe-specific JSX generation uses `production/adobe/jsx_gen.py`.