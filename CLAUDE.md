# bootlogix — Workspace Constitution

> Authored: 2026-04-07
> Version: 1.1.0
> Type: Personal workspace constitution (SDD-compliant)

---

## 1. Identity

**This workspace** is the operational center for Muhammad Tayyab — a skills hub, automation toolkit, and content production engine.

**Core mission:** Once a skill is defined, it must apply across all future sessions without manual reconfiguration. Build for reuse, not repetition.

**The workspace has two operational modes:**

| Mode | When |
|------|------|
| **General Agent** | Arbitrary software engineering, scripting, research, automation tasks |
| **Video Production Agent** | End-to-end viral Shorts production via the SSD Pipeline |

All other skills (TTS, copywriting, frontend, browser automation, MCP building) serve one of these two modes.

---

## 2. Principles

These principles are never overridden by task instructions:

1. **Skills are the authority.** When a task matches a skill's domain, follow the skill's guidance exactly. Do not re-derive conventions from scratch.
2. **Specs precede code.** For any non-trivial task, write the spec before touching production code.
3. **Conversations have memory.** Use the persistent memory system (`~/.claude/projects/-home-muhammad-tayyab-bootlogix/memory/`) to record user preferences, project context, and feedback that survives session boundaries.
4. **Distinguish modes.** General agent tasks and video production tasks follow different pipelines. Apply the right one.
5. **No aesthetic slop.** Frontend outputs must be distinctive, production-grade, and never use generic AI aesthetics (purple gradients on white, Inter/Roboto/Arial, Space Grotesk).
6. **Type safety always.** TypeScript: strict mode, no `any`, Zod for runtime validation. Python: ruff + mypy strict mode.

---

## 3. Phase Flow (SDD)

Every non-trivial task follows this four-phase workflow:

```
Constitution ──► Specify ──► Plan ──► Tasks
```

### Phase 1: Constitution
Establish the governing rules for a project or task. When starting a new project type, write a project-specific CLAUDE.md section or a dedicated constitution file. The workspace constitution (this file) is the top layer — project constitutions inherit from it.

### Phase 2: Specify
Define the deliverable in concrete terms:
- What gets produced (file, artifact, system)
- What it must do and what it must not do
- What "done" looks like (acceptance criteria)

### Phase 3: Plan
Break the work into dependency-ordered tasks. Identify which tasks can run in parallel and which must be sequential. Commit after each atomic unit of work.

### Phase 4: Tasks
Execute the plan. Each task produces a named artifact. When a subagent completes a task, it reports to the main agent, who verifies before proceeding.

---

## 4. Prompt Patterns (SDD)

Apply these six patterns by context:

### Parallel Research
When research has independent subtasks, spin up multiple subagents concurrently. Merge findings before synthesis.

### Spec-First
When asked to produce a document, report, or write-up, draft the spec before drafting the content. The spec IS the deliverable.

### Interview
Before implementing anything non-trivial, use the `interview` skill to surface the WHY behind the WHAT. Do not assume you understand the problem without asking.

### Task Delegation
Break work into subagent-sized tasks. Each task is assigned to a subagent, commits its artifact, and reports completion before the next dependent task begins.

### Constitution
When starting a new project type or domain, write a governing constitution before writing any code. The constitution outlasts the session.

### Role Assignment
For complex multi-step tasks, designate the main agent as orchestrator and subagents as specialists. Subagents receive their role, context, and constraints explicitly in the task prompt.

---

## 5. Skill Map

### Skill Directory Strategy
- **`.claude/skills/`** — installed, production-ready skills sourced from external repositories
- **`.agents/skills/`** — project-specific agents and their associated skills
- **`~/.claude/skills/`** — tools owned externally, referenced via MCP

### Installed Skills

| Skill | Location | Purpose |
|-------|----------|---------|
| ai-video-generation | `.claude/skills/` | 40+ AI video models via `infsh` CLI |
| elevenlabs-tts | `.claude/skills/` | Premium TTS, 22+ voices |
| copywriting | `.claude/skills/` | Conversion copywriting for marketing pages |
| python-code-style | `.claude/skills/` | Ruff, mypy, Google-style docstrings |
| remotion | `.claude/skills/` | Video production with Remotion |
| interview | `.claude/skills/` | Discovery conversation framework |
| find-skills | `.claude/skills/` | Skills ecosystem discovery |
| remotion-best-practices | `.agents/skills/` | 37 Remotion rule files (project-specific) |

### Skill Priority (Video Mode)
When the workspace is in **Video Production mode**, skills are invoked in this order:

1. `ai-video-generation` — model selection, footage generation
2. `elevenlabs-tts` — voiceover narration
3. `remotion` — overlay composition, timing, text animations
4. `copywriting` — script writing, narrative structure

---

## 6. SSD Pipeline (Video Mode)

For viral Shorts production, the workspace follows the SSD pipeline:

```
S ──► S ──► D ──► G
earch  cript  esign  enerate
```

Full details are in **`bootlogix-video-constitution.md`**. That document is the authoritative spec for video production — this CLAUDE.md provides the governance layer above it.

---

## 7. Conventions

### File Paths
- Workspace root: `/home/muhammad_tayyab/bootlogix`
- Temp files: `/tmp`
- Never write test files or temp files into skill directories
- Use `$SKILL_DIR` as a variable for relocatable skill paths

### Code Quality

**Python:**
- Formatter: `ruff`, Type checker: `mypy` strict mode
- Line length: 120 characters
- Docstring style: Google-style
- Min version: 3.12

**TypeScript / Node:**
- Strict mode, no `any`, `async/await` everywhere
- Runtime validation: Zod
- Transport: Streamable HTTP (remote), stdio (local)

### Frontend Aesthetics
- **Avoid:** Inter, Roboto, Arial, Space Grotesk, purple gradients on white, cookie-cutter design
- **Prefer:** Distinctive typography, bold aesthetic direction, CSS-only animations where possible

### Git
Personal workspace — conventional commits, no strict enforcement.

---

## 8. Artifact Ownership

What gets committed:
- All source code, skills, configs, and production scripts
- The `output/` directory for completed video projects

What stays local (not committed):
- `/tmp/` files
- `__pycache__/`, `*.pyc`, `.env`, `node_modules/`, `.DS_Store` (handled by `.gitignore`)
- MCP server implementations not owned by this workspace

---

## 9. Adding New Skills

1. Create the skill under `.claude/skills/<skill-name>/` or `.agents/skills/<skill-name>/` depending on scope
2. Add entry to `skills-lock.json` with source repository and computed hash
3. Add entry to `skills-manifest.json` with triggers, tools, dependencies, related skills
4. Update this constitution if the new skill introduces a new operational mode

---

## 10. What Not to Do

- Do not use `any` type in TypeScript — use `unknown` and narrow it
- Do not use `sleep` to wait for async operations — use proper wait strategies
- Do not hardcode absolute paths that should be relative
- Do not use purple-gradient-on-white aesthetics
- Do not write tests inside skill directories
- Do not invoke skills you haven't read — always read the SKILL.md first

---

## 11. Revision Log

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-04-07 | Initial workspace constitution |
| 1.1.0 | 2026-04-07 | SDD-compliant rewrite — added phase flow, prompt patterns, skill map, artifact ownership |
