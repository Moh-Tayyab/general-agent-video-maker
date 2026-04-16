# 🎬 Muhammad Edits — YouTube Shorts Automation Engine

> **Workspace Version:** 1.2.0  
> **Owner:** Muhammad Tayyab  
> **Built With:** Claude Code, FFmpeg, Google Veo 3.1, YouTube Data API v3  
> **Live:** [youtube.com/@MuhammadEdits](https://youtube.com/@MuhammadEdits)  
> **First Video Uploaded:** 2026-04-16 → [`Lg5wp4X-QA8`](https://youtu.be/Lg5wp4X-QA8)

---

## 🚀 What Is This?

A **fully autonomous YouTube Shorts production engine** that takes a reference video and produces a fully edited, SEO-optimized, YouTube-uploaded Short — without manual intervention.

```
Drop a reference video
        ↓
AI analyzes beats, cuts, color grade, text overlays
        ↓
AI writes beat-synced script
        ↓
AI generates or edits footage to match style
        ↓
AI applies cinematic color grade (teal/orange)
        ↓
AI burns in beat-sync captions
        ↓
AI mixes background music
        ↓
AI uploads to YouTube with SEO
        ↓
Video goes live — fully optimized
```

**Time per video:** 10-15 minutes (vs 3-5 hours manually)

---

## 📊 Live Results

| Metric | Value |
|--------|-------|
| Videos Published | 1 |
| First Video | Tom Cruise Edit |
| Upload Date | 2026-04-16 |
| Views | Pending (just uploaded) |
| Subscribers | Growing |

---

## 🏗️ Core Architecture

### The SSD Pipeline (Search → Script → Design → Generate)

```
┌────────────────────────────────────────────────────────────────────┐
│                         SSD PIPELINE                                 │
│                                                                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │ SEARCH   │───▶│ SCRIPT   │───▶│ DESIGN   │───▶│ GENERATE │   │
│  │Researcher│    │Scriptwriter│   │Visual-Des│    │ Producer │   │
│  │ Agent    │    │ Agent     │    │  igner    │    │ Agent    │   │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘   │
│       │               │               │               │           │
│   Beat Map        Beat Sync      AI Prompts      Final Video     │
│   Scene List      Text Timing     Shot List       YouTube API     │
│   Color Hex       Energy Arc      Color Grade     Upload + SEO     │
└────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Role |
|-------|-----------|------|
| **Agent Orchestration** | Claude Code Team System | Coordinates all agents |
| **Video Processing** | FFmpeg + Production Bridges | Crop, grade, composite |
| **AI Footage** | Google Veo 3.1 via infsh CLI | Text-to-video generation |
| **TTS / Voiceover** | ElevenLabs via infsh CLI | Professional voice narration |
| **Caption Animation** | FFmpeg ASS filter | Karaoke-style beat-sync captions |
| **SEO Copywriting** | Claude copywriting skill | Titles, descriptions, hashtags |
| **YouTube Upload** | YouTube Data API v3 (OAuth 2.0) | Direct upload + metadata update |

---

## 🎬 The Tom Cruise Pipeline (Case Study)

### How It Works — Step by Step

#### Step 1: Reference Video Analyzed (SEARCH Agent)

```
Reference: https://youtube.com/shorts/7JVIRjiY4kw

Audio Analysis:
- Track: Heavenly Jumpstyle (Slowed) by TWXNY
- Original BPM: 130
- Slowed BPM: 65 (half-time)
- Beat interval: 0.92 seconds per beat

Scene Breakdown:
| Time  | Scene                    | Stunt Type          |
|-------|--------------------------|---------------------|
| 0:00  | Burj Khalifa climb      | 1,700ft extreme altitude |
| 0:08  | HALO jump               | Military freefall   |
| 0:16  | Motorcycle cliff jump    | Mid-air bike launch |
| 0:24  | Plane takeoff dangling  | Aircraft exterior   |
| 0:32  | Helicopter chase        | Urban running      |
| 0:40  | Underwater scene        | Breath-hold dive   |
| 0:48  | Final motorcycle        | Mountain road      |
| 0:56  | Outro                  | Climactic freeze   |

Color Grade Extracted:
- Shadows: Teal #008080
- Highlights: Orange #FF8C00
- Contrast: +20 (crushed blacks)
- Vignette: 25%
```

#### Step 2: Beat-Synced Script Written (SCRIPT Agent)

```
Beat Map (at 65 BPM):
| Timestamp | Beat | Text Overlay      | Animation        |
|-----------|------|-------------------|------------------|
| 0:00      | 1    | AVERAGE DAY OF    | pop-in           |
| 0:20      | 21   | HE'S NOT DONE     | pop + scale 130%  |
| 0:40      | 41   | TIL HE'S 90       | pop + scale + wiggle |
| 0:50      | 49   | @Maven-Edits      | static           |
| 0:56      | 57   | #edit #shorts     | slide-in         |

Font: Bebas Neue, 60px, white, 2px black stroke
Animation: character-by-character pop, 0.08s per char, ease-out
```

#### Step 3: AI Prompts Designed (VISUAL-DESIGNER Agent)

```
8 shots generated with google/veo-3-1-fast

Example Shot 3 — Motorcycle Cliff Jump:
"Professional stunt performer on motorcycle launching off enormous cliff 
edge into blue sky, bike angled mid-air for maximum distance, rider 
in dynamic crouch position, dust debris and gravel spraying from 
cliff face, epic scale mountain landscape background, dramatic low 
angle from canyon floor below, teal shadows orange highlights 
cinematic grade, 9:16 vertical aspect ratio 1080x1920, 4 second 
clip, dramatic low angle tracking upward"
```

#### Step 4: Video Generated & Composed (PRODUCER Agent)

```
FFmpeg Color Grade Pipeline:
1. crop=360:640:108:0,scale=1080:1920
2. eq=contrast=1.2:brightness=0.03:saturation=1.1
3. colorbalance=bs=0.15:bm=0.05:rm=0.05:rh=0.1:gh=0.03
   → Teal shadows (blue +0.15)
   → Orange highlights (red +0.1)
4. vignette=0.25

Captions Burned:
- Font: Bangers (Bebas Neue style)
- Size: 96px at 1080p
- Stroke: 6px black
- Color: White
- Karaoke animation: word-by-word pop

Audio Mix:
- Original audio: 50% volume
- BG music (Heavenly Jumpstyle Slowed): 35% volume
- Fade in: 0-1s
- Fade out: 52-54s

Final Output:
- Format: 1080x1920 (9:16 vertical)
- Codec: H.264, CRF 18
- Audio: AAC 192kbps
- Duration: 54.7s
- Size: 53MB
```

#### Step 5: SEO Optimized & Uploaded (YOUTUBE BRIDGE)

```
Title Formula:
[Emotional Hook] + [Specific Detail] + [Trending Tags]
"Tom Cruise Does The Most Insane Stunts In Real Life 🔥 #shorts #edit #viral"

Description Formula:
Line 1: Emotional hook (creates curiosity)
Line 2: Value proposition (what they get)
Line 3: Song credit
[Divider]
CTA: Subscribe
CTA: Notifications
[Divider]
#Hashtags (15 max in body)

4-Tier Hashtag Strategy:
┌─────────┬─────────────────────────────────────┬───────────┐
│ Tier    │ Hashtags                            │ Reach     │
├─────────┼─────────────────────────────────────┼───────────┤
│ Tier 1  │ #shorts #viral #trending #fyp      │ 1B+ views│
│ Tier 2  │ #tomcruise #missionimpossible      │ 100M+     │
│ Tier 3  │ #action #movie #hollywood #stunts  │ 10M+      │
│ Tier 4  │ #edit #bestedit #insane #wow #omg  │ 1M+       │
└─────────┴─────────────────────────────────────┴───────────┘

Uploaded via: YouTube Data API v3 (OAuth 2.0)
Live URL: https://youtu.be/Lg5wp4X-QA8
```

---

## 📁 Workspace Structure

```
bootlogix/                          ← Root: ~/bootlogix
│
├── README.md                       ← This file
├── CLAUDE.md                       ← Workspace constitution (SDD rules)
│
├── agents/                         ← Claude Code team agents
│   └── prompts/
│       ├── video-orchestrator.md   ← Team coordination protocol
│       ├── researcher_agent.py      ← SEARCH phase agent
│       ├── scriptwriter_agent.py    ← SCRIPT phase agent
│       ├── visual_designer_agent.py← DESIGN phase agent
│       └── producer_agent.py        ← GENERATE phase agent
│
└── production/                      ← Video production pipeline
    ├── README.md                   ← Production pipeline docs
    ├── bridges/                   ← FFmpeg + API wrappers
    │   ├── media.py               ← Crop, trim, audio mix
    │   ├── color.py                ← Cinematic color grading
    │   ├── captions.py             ← SRT → ASS karaoke converter
    │   ├── render.py               ← FFmpeg encode + caption burn-in
    │   ├── youtube.py              ← YouTube API upload bridge
    │   └── payload.py             ← TTS + video prompt prep
    ├── validation/
    │   └── quality.py              ← ffprobe quality gates
    ├── adobe/
    │   ├── jsx_gen.py             ← Premiere/AE JSX automation
    │   ├── premiere_agent.py       ← Adobe Premiere automation
    │   └── aftereffects_agent.py   ← After Effects automation
    ├── output/
    │   └── tom_cruise_maven_edit/
    │       └── final_video.mp4    ← First published video
    └── secrets/
        ├── client_secrets.json     ← Google OAuth (DO NOT SHARE)
        └── youtube_credentials.json← Persistent tokens (auto-refresh)
```

---

## 🛠️ How to Run

### Full Pipeline (End-to-End)

```bash
# Drop reference video + source footage + music
# The agents handle everything automatically

cd ~/bootlogix
claude --prompt "Run the full SSD pipeline for my new video"
```

### Manual YouTube Upload (Any Video)

```python
from production.bridges.youtube import YouTubeBridge

yt = YouTubeBridge("production/secrets/client_secrets.json")
yt.authenticate()  # Opens browser for OAuth (one-time only)

result = yt.upload(
    video_path="/path/to/video.mp4",
    title="Amazing Video 🔥 #shorts #viral",
    description="Your SEO-optimized description...",
    tags=["viral", "trending", "fyp", ...],
    privacy_status="public"
)

print(result["video_url"])
```

---

## 🔑 Key Features

### Why This Pipeline Is Different

| Typical Automation | Muhammad Edits Pipeline |
|-------------------|----------------------|
| Random cuts on random beats | Frame-accurate beat sync (0.92s intervals) |
| Generic color grade | Teal-orange cinematic (exact hex values) |
| Basic text overlay | Character-pop animation on exact beat |
| Random hashtags | 4-tier hashtag strategy with trending data |
| Manual upload | Full YouTube API with OAuth |
| One-time setup | Persistent credentials (auto-refresh) |
| Single video only | Scalable batch processing |

### What's Unique About This Workspace

1. **Persistent Memory** — Every session learns. Your preferences, feedback, and project context survive session boundaries via the memory system.

2. **Skills as Authority** — When a task matches a skill's domain, the skill's guidance is followed exactly — no re-deriving conventions.

3. **SDD-Compliant** — Every non-trivial task follows: Constitution → Specify → Plan → Tasks.

4. **Type Safety** — Python: ruff + mypy strict. TypeScript: strict mode, no `any`, Zod for runtime validation.

---

## 🔮 Future Roadmap

```
Phase 5 ─── Watch Folder Automation
│           Monitor folder → auto-process → auto-upload
│
Phase 6 ─── AI Thumbnail Generation
│           Best frame → FLUX.1/DALL-E → Bold text → Auto-upload
│
Phase 7 ─── SEO Auto-Optimizer
│           Trending topics API → Title A/B test → Winning title
│
Phase 8 ─── Multi-Platform Distribution
│           Single edit → YouTube + IG Reels + TikTok + Twitter
│
Phase 9 ─── Content Calendar
│           Batch footage → 30-day scheduler → Auto-post at optimal times
```

---

## 🧠 Memory & Knowledge Base

Key decisions and context that persist across sessions:

| Memory | What It Means |
|--------|--------------|
| `video-production-tools-audit` | Audit of all video gen tools + infsh status |
| `spec-driven-development` | SDD methodology: specs as primary artifact |

Located at: `~/.claude/projects/-home-muhammad-tayyab-bootlogix/memory/`

---

## 📜 Revision History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-04-07 | Initial workspace setup |
| 1.1.0 | 2026-04-07 | SDD-compliant rewrite, phase flow, skills |
| 1.2.0 | 2026-04-15 | Video pipeline team, agent prompts, production utilities |
| 1.3.0 | 2026-04-16 | Full YouTube API integration, first video published |

---

**Built with:** Claude Code · FFmpeg · Google Veo 3.1 · YouTube Data API v3  
**Author:** Muhammad Tayyab  
**GitHub:** github.com/moh-tayyab  
**YouTube:** youtube.com/@MuhammadEdits  
**Live Video:** [https://youtu.be/Lg5wp4X-QA8](https://youtu.be/Lg5wp4X-QA8)
