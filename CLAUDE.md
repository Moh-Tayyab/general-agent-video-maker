# bootlogix

Personal Claude Code workspace — a skills hub and automation toolkit.

## Who This Is

This workspace belongs to Muhammad Tayyab. It is the operational center for content production, software engineering, and AI-assisted automation. Everything here is built for reuse: once a skill is defined, it should apply across all future sessions without manual reconfiguration.

## What Lives Here

| Area | Description |
|------|-------------|
| `.agents/skills/` | 9 reusable skills — video generation, TTS, copywriting, frontend design, MCP building, browser automation, code style |
| `playwright-skill/` | Functional Node.js browser automation tool with a 442-line helper library |
| `.mcp.json` | MCP server config — YouTube Shorts transcript extraction via Playwright |
| `skills-lock.json` | Integrity-tracked registry of all external skill sources |

## How to Work Here

### First, Understand the Task

Before writing any code or invoking any skill, read the full CLAUDE.md and any relevant skill files. The skills here encode domain knowledge — use them before improvising.

### Choose the Right Skill

- **Video content** → `ai-video-generation`, `elevenlabs-tts`
- **Marketing copy** → `copywriting`
- **Frontend / UI** → `frontend-design`, `web-design-guidelines`
- **Browser automation** → `playwright-skill`
- **Building MCP servers** → `mcp-builder`
- **Python code** → `python-code-style`
- **JavaScript / TypeScript** → `javascript-typescript-jest`

### Skills Take Precedence

When a skill exists for a task, follow the skill's guidance exactly. Do not re-derive conventions from scratch when a skill already encodes them.

### MCP Tools Are Always Available

The YouTube Shorts transcript extractor is always accessible via the `mcp__youtube-shorts-transcript-extractor__extract_youtube_shorts_transcript` tool. Use it before transcribing manually.

## Conventions

### File Paths

- Always resolve paths from the workspace root: `/home/muhammad_tayyab/bootlogix`
- Use `$SKILL_DIR` as a variable when a skill can be installed in multiple locations
- Never write test files or temporary files into skill directories — use `/tmp`

### Code Quality

- Python: `ruff` + `mypy` strict mode, 120-char line length, Google-style docstrings
- TypeScript/Node: strict mode, no `any`, `async/await` everywhere, Zod for runtime validation
- Frontend: production-grade, distinctive aesthetics — never generic "AI slop"

### Git

This is a personal workspace, not a shared repository. Use conventional commits but do not enforce a strict workflow.

## Adding New Skills

1. Create the skill under `.agents/skills/<skill-name>/SKILL.md`
2. Add an entry to `skills-lock.json` with source and computed hash
3. Document the skill in `skills-manifest.json`
4. Run `bootstrap-skill.sh <skill-name>` if the skill follows standard conventions

## What Not to Do

- Do not write tests inside skill directories
- Do not hardcode absolute paths that should be relative
- Do not use `any` type in TypeScript — use `unknown` and narrow it
- Do not use purple-gradient-on-white aesthetics in any frontend work
- Do not use `sleep` to wait for async operations — use proper wait strategies
