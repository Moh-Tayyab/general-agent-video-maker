# 🎬 Muhammad Edits — YouTube Shorts Automation Pipeline

> **Version:** 1.0.0  
> **Author:** Muhammad Tayyab  
> **Last Updated:** 2026-04-16  
> **Status:** Production Ready

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Pipeline Phases](#3-pipeline-phases)
   - [Phase 1: SEARCH (Research Agent)](#phase-1-search)
   - [Phase 2: SCRIPT (Scriptwriter Agent)](#phase-2-script)
   - [Phase 3: DESIGN (Visual Designer Agent)](#phase-3-design)
   - [Phase 4: GENERATE (Producer Agent)](#phase-4-generate)
4. [YouTube API Integration](#4-youtube-api-integration)
5. [SEO Strategy](#5-seo-strategy)
6. [File Structure](#6-file-structure)
7. [Setup & Installation](#7-setup--installation)
8. [How to Run](#8-how-to-run)
9. [Future Roadmap](#9-future-roadmap)

---

## 1. Project Overview

### What Is This?

A fully automated, agentic YouTube Shorts production pipeline. Drop a reference video + source footage + background music, and the system:

1. **Analyzes** the reference video style (beats, cuts, color grade, text overlays)
2. **Writes** a beat-synced script matched to the music
3. **Designs** AI video generation prompts for each scene
4. **Generates** or edits footage to match the style
5. **Composes** the final video with cinematic color grading
6. **Uploads** directly to YouTube with fully optimized SEO

### The Problem It Solves

| Manual Process | Automated Pipeline |
|---------------|-------------------|
| 3-5 hours per video | 10-15 minutes per video |
| Inconsistent quality | Consistent Maven-Edit style |
| Manual SEO research | AI-powered hashtag optimization |
| Manual YouTube upload | One-click YouTube API upload |
| No scaling | Batch process unlimited videos |

---

## 2. Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INPUTS                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Reference   │  │   Source      │  │   Background  │                  │
│  │  Video       │  │   Footage     │  │   Music       │                  │
│  │  (Maven-Edit)│  │  (Original)   │  │  (MP3/WAV)    │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
└─────────┼─────────────────┼─────────────────┼───────────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     SSD PIPELINE (Agents)                                │
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐               │
│  │  RESEARCHER  │───▶│ SCRIPTWRITER │───▶│VISUAL-DESIGN│              │
│  │  (SEARCH)   │    │  (SCRIPT)   │    │  (DESIGN)   │              │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘               │
│         │                   │                   │                       │
│         │         BEAT MAP + SCRIPT + SHOT LIST │                       │
│         │                   │                   │                       │
│         │                   │                   ▼                       │
│         │                   │           ┌─────────────┐                 │
│         │                   └──────────▶│  PRODUCER   │                 │
│         │                               │  (GENERATE) │                 │
│         │                               └──────┬──────┘                 │
│         │                                      │                         │
│         │         8 AI CLIPS + AUDIO MIX + GRADE                       │
│         │                                      │                         │
│         │                                      ▼                         │
│         │                               ┌─────────────┐                 │
│         │                               │   YOUTUBE   │                 │
│         │                               │   BRIDGE    │                 │
│         │                               └──────┬──────┘                 │
└─────────┼──────────────────────────────────────┼────────────────────────┘
          │                                      │
          ▼                                      ▼
┌──────────────────────┐         ┌──────────────────────────┐
│   REFERENCE ARTIFACTS │         │   FINAL OUTPUT           │
│  /tmp/bootlogix_*    │         │  YouTube: Lg5wp4X-QA8   │
│  research.md         │         │  1080x1920 60fps 53MB   │
│  script.md           │         │  Public, SEO Optimized  │
│  design.md           │         └──────────────────────────┘
│  shotlist.json       │
└──────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Orchestration** | Claude Code (Team System) | Multi-agent coordination |
| **Video Editing** | FFmpeg + Production Bridges | Crop, grade, composite |
| **AI Footage** | Google Veo 3.1 via infsh CLI | Text-to-video generation |
| **Text-to-Speech** | ElevenLabs via infsh CLI | Narration generation |
| **Caption Burn-in** | FFmpeg ASS filter | Karaoke-style captions |
| **SEO** | Claude copywriting skill | Title, description, hashtags |
| **YouTube Upload** | YouTube Data API v3 | Direct upload + metadata |

---

## 3. Pipeline Phases

### Phase 1: SEARCH (Researcher Agent)

**Goal:** Extract every measurable detail from the reference video.

#### What It Does:

```
1. Downloads the reference YouTube Short via yt-dlp
2. Extracts audio waveform and beat markers
3. Identifies exact scene transitions and timestamps
4. Analyzes color grade values (teal/orange hex codes)
5. Identifies text overlays (font, size, animation, timing)
6. Maps the full energy arc of the video
7. Researches the background music (BPM, key, beatmap)
```

#### Output Artifact: `/tmp/bootlogix_research.md`

```markdown
## Audio Analysis
- Track: Heavenly Jumpstyle (Slowed)
- Original BPM: 130 (TWXNY)
- Slowed BPM: ~65 (half-time)
- Beat interval: 0.92s per beat

## Beat Markers
| Timestamp | Beat | Phase |
|-----------|------|-------|
| 0:00 | 1 | INTRO |
| 0:20 | 21 | FIRST DROP |
| 0:40 | 41 | SECOND DROP |

## Scene Breakdown
| Time | Clip | Stunt |
|------|------|-------|
| 0:00-0:08 | Burj Khalifa climb | Extreme altitude |
| 0:08-0:16 | HALO jump | Military freefall |

## Color Grade
- Shadows: Teal #008080
- Highlights: Orange #FF8C00
- Contrast: +20 (crushed blacks)
- Vignette: 25%

## Text Overlays
- Font: Bebas Neue, 60px
- Animation: character-pop on beat
- Stroke: 2px black
```

#### Why This Matters:

A human editor would watch the reference video and "feel" the timing. The SEARCH phase gives every agent **exact numerical values** — no guessing, no approximation.

---

### Phase 2: SCRIPT (Scriptwriter Agent)

**Goal:** Map a narrative arc to the beat markers.

#### What It Does:

```
1. Reads the research artifact
2. Identifies the beat map (every 0.92s at 65 BPM)
3. Places text overlays at peak emotional moments (beats 21, 41)
4. Writes punchlines that sync to the drops
5. Structures intro/build/drop/outro timing
```

#### Beat Sync Table:

| Timestamp | Beat | Overlay | Animation |
|-----------|------|---------|-----------|
| 0:00 | 1 | "AVERAGE DAY OF" | pop-in |
| 0:20 | 21 | "HE'S NOT DONE" | pop + scale 130% |
| 0:40 | 41 | "TIL HE'S 90" | pop + scale + wiggle |
| 0:50 | 49 | "@Maven-Edits" | static |
| 0:56 | 57 | "#edit #shorts" | slide-in |

#### Font/Style Spec (From Script):

```css
font-family: "Bebas Neue", Impact, sans-serif;
font-size: 60px;
color: #FFFFFF;
stroke: 2px #000000;
animation-pop: scale 100% → 130% → 100%, 0.3s ease-out;
animation-char-pop: 0.08s per character, sequential;
```

#### Why Bebas Neue?

It's the **definitive Shorts font** — bold, condensed, all-caps, instantly recognizable. Used by every major action movie edit creator on Shorts.

---

### Phase 3: DESIGN (Visual Designer Agent)

**Goal:** Create AI generation prompts for every scene.

#### What It Does:

```
1. Takes the beat map and scene list from SEARCH
2. Writes detailed AI video prompts for each of 8 scenes
3. Specifies: subject, camera angle, lighting, motion, color grade
4. Assigns each prompt a camera movement type
5. Outputs a machine-readable shot list JSON
```

#### The 8 Shots:

| Shot | Time | Scene | Camera | AI Prompt Summary |
|------|------|-------|--------|------------------|
| 1 | 0:00-0:08 | Burj Khalifa climb | Low angle tracking ascending | Man in tactical suit scaling 1,700ft glass skyscraper, teal-orange cinematic grade |
| 2 | 0:08-0:16 | HALO jump | POV helmet | Military freefall through clouds, parachute deploy, first-person perspective |
| 3 | 0:16-0:24 | Motorcycle cliff | Low angle from canyon floor | Stunt performer on motorcycle launching off cliff, dust spray, dramatic low angle |
| 4 | 0:24-0:32 | Plane dangling | High angle side | Person clinging to aircraft exterior during takeoff, orange engine glow |
| 5 | 0:32-0:40 | Helicopter chase | Tracking handheld | Man sprinting through streets, helicopter overhead, handheld jitter |
| 6 | 0:40-0:48 | Underwater | Low angle upward | Deep underwater diver, light beams, teal-dominant palette |
| 7 | 0:48-0:56 | Final motorcycle | Rear tracking | Motorcycle leaning into mountain curve, gravel spray, orange dust trail |
| 8 | 0:56-1:00 | Outro | Cinematic wide | Climactic freeze-frame pose, smoke/dust atmosphere, heavy vignette |

#### Example AI Prompt (Shot 3):

```
Professional stunt performer on motorcycle launching off enormous cliff 
edge into blue sky, bike angled mid-air for maximum distance, rider 
in dynamic crouch position, dust debris and gravel spraying from cliff 
face, epic scale mountain landscape background, dramatic low angle 
from canyon floor below, teal shadows orange highlights cinematic grade, 
9:16 vertical aspect ratio 1080x1920, 4 second clip, dramatic low 
angle tracking upward
```

#### Output: `/tmp/bootlogix_shotlist.json`

```json
{
  "project": "Tom Cruise Beat-Sync Edit",
  "version": "1.0",
  "aspect_ratio": "9:16",
  "resolution": "1080x1920",
  "total_duration_seconds": 60,
  "bpm": 65,
  "shots": [
    {
      "shot_number": 1,
      "timestamp_start": "0:00",
      "timestamp_end": "0:08",
      "scene": "Burj Khalifa climb",
      "ai_prompt": "A man in dark tactical...",
      "camera": "low angle tracking shot ascending",
      "duration_seconds": 4,
      "motion_indicators": ["ascending", "wind billowing", "gripping"],
      "beat_number": 1,
      "phase": "INTRO"
    }
  ]
}
```

---

### Phase 4: GENERATE (Producer Agent)

**Goal:** Execute all generation + compose the final video.

#### What It Does:

```
Step 1: Set up output directories
        /tmp/bootlogix_output/   → final renders
        /tmp/bootlogix_audio/    → music tracks
        /tmp/bootlogix_clips/    → generated footage

Step 2: Download/verify background music
        - yt-dlp to extract audio from reference
        - Verify BPM and beat structure

Step 3: Generate AI video clips (via infsh CLI)
        infsh app run google/veo-3-1-fast \
          --input '{"prompt": "...", "duration": 4, "aspect_ratio": "9:16"}'

Step 4: Compose video with FFmpeg
        - Concatenate all 8 clips
        - Apply teal-orange color grade
        - Add Ken Burns zoom keyframes
        - Burn in ASS captions (beat-synced)

Step 5: Mix audio
        - Original audio at 50% volume
        - Background music at 35% volume
        - Audio fade in (0-1s), fade out (52-54s)

Step 6: Export final video
        - 1080x1920 (9:16 vertical)
        - H.264 codec, CRF 18
        - AAC audio 192kbps
        - 53MB final file
```

#### Color Grading Pipeline (FFmpeg):

```bash
# Step 1: Crop and scale
crop=360:640:108:0,scale=1080:1920

# Step 2: Cinematic grade
eq=contrast=1.2:brightness=0.03:saturation=1.1

# Step 3: Teal-orange color balance
# Blue in shadows (+0.15), red in highlights (+0.1)
colorbalance=bs=0.15:bm=0.05:rm=0.05:rh=0.1:gh=0.03

# Step 4: Vignette (darken corners)
vignette=0.25
```

**Why this exact formula?**
- `bs=0.15` (blue in shadows) → Teal shadows
- `rh=0.1` (red in highlights) → Orange highlights
- `contrast=1.2` → Deep, cinematic blacks
- `vignette=0.25` → Draws eye to center action

---

## 4. YouTube API Integration

### OAuth Flow Explained

The YouTube Data API v3 requires **OAuth 2.0** authentication to upload videos on behalf of a channel. Here's the complete flow:

```
┌─────────────────────────────────────────────────────────┐
│  1. CREDENTIALS SETUP (One-time)                        │
│                                                         │
│  Google Cloud Console → APIs & Services → Credentials    │
│  Create OAuth 2.0 Client ID (Desktop App)               │
│  Download client_secrets.json                            │
└─────────────────────────┬───────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  2. FIRST-TIME AUTHORIZATION (Manual)                    │
│                                                         │
│  User visits auth URL                                    │
│  → Signs in to Google                                   │
│  → Grants "Manage YouTube Account" permission           │
│  → Redirects to localhost with auth CODE                 │
│  → Code exchanged for REFRESH TOKEN                     │
│  → Refresh token saved to youtube_credentials.json       │
└─────────────────────────┬───────────────────────────────┘
                        │
                        │ (Tokens saved permanently)
                        ▼
┌─────────────────────────────────────────────────────────┐
│  3. AUTOMATIC UPLOADS (Every time)                       │
│                                                         │
│  Script loads credentials.json                           │
│  → Checks if token expired                              │
│  → If expired: auto-refreshes using refresh_token       │
│  → If valid: uses access_token directly                  │
│  → No manual intervention needed                         │
└─────────────────────────────────────────────────────────┘
```

### Scopes Used

| Scope | Purpose |
|-------|---------|
| `https://www.googleapis.com/auth/youtube.upload` | Upload new videos |
| `https://www.googleapis.com/auth/youtube` | Full YouTube access (update metadata) |

### Why Both Scopes?

- **`youtube.upload`** — Required to upload the video file initially
- **`youtube`** — Required to UPDATE the video metadata (title, description, tags) AFTER upload

Without the full `youtube` scope, we can upload but cannot update SEO.

### Credentials Storage

```
/home/muhammad_tayyab/bootlogix/production/secrets/
├── client_secrets.json              ← Google Cloud OAuth (DO NOT SHARE)
└── youtube_credentials.json         ← Persistent tokens (auto-refresh)
```

### YouTube Bridge (`production/bridges/youtube.py`)

The `YouTubeBridge` class handles all API interactions:

```python
class YouTubeBridge:
    def authenticate(self)      # OAuth flow + token refresh
    def get_channel_info(self)  # Fetch channel details
    def upload(self, ...)       # Upload video + metadata
```

**Key Methods:**

```python
# Upload with full SEO
result = youtube.upload(
    video_path="/path/to/video.mp4",
    title="Tom Cruise Does The Most Insane Stunts 🔥 #shorts",
    description="Full SEO-optimized description...",
    tags=["viral", "tomcruise", "action", ...],
    category_id="22",           # People & Blogs
    privacy_status="public",    # public/private/unlisted
    thumbnail_path="/path/to/thumb.jpg"  # Optional
)

# Result:
{
    "success": True,
    "video_id": "Lg5wp4X-QA8",
    "video_url": "https://youtu.be/Lg5wp4X-QA8"
}
```

---

## 5. SEO Strategy

### Title Formula

```
[Emotional Hook] + [Specific Detail] + [Trending Format]
     ↓                    ↓                   ↓
"Tom Cruise"    + "Most Insane Stunts" + "🔥 #shorts #viral"
```

**Rules:**
- Front-load the most important keyword (Tom Cruise)
- Use 1-2 emoji maximum (🔥 works for action content)
- Always include `#shorts` in the title
- Max length: 70 characters

### Description Formula

```
Line 1: [ Emotional hook — creates curiosity ]
Line 2: [ Value proposition — what they get ]
Line 3: [ Song credit if applicable ]

[Divider: "━━━━━━"]

Line 4:  [ CTA: Subscribe ]
Line 5:  [ CTA: Notifications ]

[Divider]

#Hashtags (max 15 in description body)
```

### Hashtag Strategy (The 4-Tier System)

| Tier | Hashtags | Views | Purpose |
|------|----------|-------|---------|
| **Tier 1** | `#shorts` `#viral` `#trending` `#fyp` `#foryou` | 1B+ | Algorithm triggers |
| **Tier 2** | `#tomcruise` `#missionimpossible` `#action` `#movie` `#hollywood` | 100M+ | Niche targeting |
| **Tier 3** | `#edit` `#bestedit` `#viraledit` `#clips` | 10M+ | Community discovery |
| **Tier 4** | `#insane` `#wow` `#omg` `#crazy` | 1M+ | Emotional triggers |

**Golden Rule:** Never use hashtags only from one tier. Mix all four.

**Hashtags NOT to use:**
- `#subscribe` — suppressed by algorithm
- `#likeforlike` — spam signal
- Anything with more than 15 characters

### Tag Optimization

YouTube treats tags differently from hashtags:
- **Tags** = internal keywords for search (not visible to users)
- **Hashtags** = visible in description, indexed by YouTube Search

We use **25 tags** combining:
- Exact-match keywords (`tom cruise edit`)
- Broader keywords (`action movie`)
- Misspellings people might use (`tomcruise`)
- Trending terms (`shorts viral`)

---

## 6. File Structure

```
/home/muhammad_tayyab/bootlogix/
├── CLAUDE.md                          # Workspace constitution
├── agents/
│   └── prompts/
│       ├── video-orchestrator.md       # Team coordination guide
│       ├── researcher_agent.py         # SEARCH agent prompt
│       ├── scriptwriter_agent.py      # SCRIPT agent prompt
│       ├── visual_designer_agent.py   # DESIGN agent prompt
│       └── producer_agent.py          # GENERATE agent prompt
│
└── production/
    ├── README.md                      # This file
    ├── bridges/
    │   ├── __init__.py
    │   ├── media.py                   # Crop, trim, audio mix
    │   ├── color.py                   # Cinematic color grading
    │   ├── captions.py                # SRT → ASS karaoke
    │   ├── render.py                  # FFmpeg encode + burn-in
    │   ├── youtube.py                 # YouTube API upload
    │   └── payload.py                 # TTS + video prompt prep
    ├── validation/
    │   └── quality.py                 # ffprobe quality gates
    ├── adobe/
    │   ├── jsx_gen.py                # Premiere/AE JSX automation
    │   └── (other Adobe utilities)
    ├── output/
    │   └── tom_cruise_maven_edit/
    │       ├── final_video.mp4        ← FINAL OUTPUT
    │       ├── step1_cropped.mp4
    │       └── step2_graded.mp4
    └── secrets/
        ├── client_secrets.json        ← OAuth credentials
        └── youtube_credentials.json    ← Persistent tokens
```

### Temporary Artifacts (at `/tmp/`)

```
/tmp/
├── bootlogix_research.md              ← Phase 1 output
├── bootlogix_script.md                ← Phase 2 output
├── bootlogix_design.md                ← Phase 3 output
├── bootlogix_shotlist.json            ← Phase 3 output
├── bootlogix_audio/
│   └── heavenly.mp3                  ← Background music
├── bootlogix_clips/
│   ├── shot_1.mp4                    ← AI-generated clip 1
│   ├── shot_2.mp4                    ← AI-generated clip 2
│   └── ... (8 total)
├── final_edit/
│   ├── maven_captions.ass             ← Beat-sync captions
│   ├── tom_cruise_edit_final.mp4     ← Pre-upload final
│   └── filter_complex.txt            ← FFmpeg filter graph
└── ref_video.mp4                      ← Downloaded reference
```

---

## 7. Setup & Installation

### Prerequisites

```bash
# Core tools
Python 3.12+
ffmpeg (with libx264, libass, libmp3lame)
git

# Python packages
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

# CLI tools
pip install inference-sh  # AI video generation
yt-dlp                   # Video download
```

### Google Cloud Setup (One-Time)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create new project: `youtube-automation`
3. Enable: **YouTube Data API v3**
4. Go to **APIs & Services → Credentials**
5. Create **OAuth Client ID** (Desktop App)
6. Download JSON → save as `client_secrets.json`
7. Move to `production/secrets/client_secrets.json`
8. Go to **OAuth consent screen**
   - User type: **External**
   - Scopes: `https://www.googleapis.com/auth/youtube.upload`
9. Add test user: `your-email@gmail.com`

### Directory Setup

```bash
mkdir -p ~/bootlogix/production/secrets
mkdir -p ~/bootlogix/production/output
mkdir -p /tmp/bootlogix_audio
mkdir -p /tmp/bootlogix_clips
mkdir -p /tmp/final_edit
```

---

## 8. How to Run

### Full Pipeline (End-to-End)

```bash
# 1. Start the team pipeline
cd ~/bootlogix
python3 -c "
from agents.video_pipeline import run_pipeline
run_pipeline(
    reference_video='https://youtube.com/shorts/XXXXX',
    source_footage='/path/to/footage.mp4',
    background_music='/path/to/music.mp3'
)
"
```

### Individual Phases

```bash
# Phase 1: Research only
python3 /tmp/agents/researcher_agent.py

# Phase 2: Script only (after research)
python3 /tmp/agents/scriptwriter_agent.py

# Phase 3: Design only (after script)
python3 /tmp/agents/visual_designer_agent.py

# Phase 4: Generate + Upload (after design)
python3 /tmp/agents/producer_agent.py
```

### Manual YouTube Upload (Without Full Pipeline)

```bash
# Upload any video with SEO
python3 << 'EOF'
from production.bridges.youtube import YouTubeBridge

yt = YouTubeBridge("/path/to/client_secrets.json")

# First time: opens browser for OAuth
# After: uses saved credentials
yt.authenticate()

result = yt.upload(
    video_path="/path/to/video.mp4",
    title="Your Video Title 🔥 #shorts",
    description="SEO-optimized description...",
    tags=["tag1", "tag2", "..."],
    privacy_status="public"
)

print(result["video_url"])
EOF
```

### Watch Folder Automation (Future)

```bash
# Monitor folder for new videos
inotifywait -m /path/to/watch/folder -e create | while read file; do
    python3 /tmp/auto_edit.py "$file"
done
```

---

## 9. Future Roadmap

### Phase 5: Watch Folder Automation

```python
"""
When a video is dropped in /watch/folder/:
1. Detect new file (inotifywait)
2. Run full SSD pipeline automatically
3. Upload to YouTube
4. Send Telegram/Discord notification with link
5. Log to production/history.md
"""
```

### Phase 6: AI Thumbnail Generation

```
Reference Frame (best frame from video)
    ↓
FLUX.1 or DALL-E 3 API
    ↓
Add bold text overlay (Bebas Neue)
    ↓
YouTube thumbnail (1280x720)
    ↓
Upload via YouTube API
```

### Phase 7: SEO Auto-Optimizer

```
YouTube Data API → Fetch trending topics
    ↓
Claude → Generate 5 title options
    ↓
A/B test: Upload same video with different titles
    ↓
Analytics → Pick winning title
    ↓
Update video with best-performing title
```

### Phase 8: Multi-Platform Distribution

```
Single Edit Pipeline
    ├── YouTube Shorts (9:16, 60s)
    ├── Instagram Reels (1:1, 30s)
    ├── TikTok (9:16, 60s)
    └── Twitter/X (16:4, 60s)
```

### Phase 9: Content Calendar

```
User inputs: niche, posting frequency, batch of raw footage
    ↓
Claude → Schedules 30-day content calendar
    ↓
System → Auto-edits and queues videos
    ↓
Scheduler → Posts at optimal times (from analytics)
    ↓
Analytics → Reports performance weekly
```

---

## 🏆 What Makes This Pipeline Different

| Typical Automation | Muhammad Edits Pipeline |
|-------------------|------------------------|
| Random cuts on random beats | Exact frame-accurate beat sync |
| Generic color grade | Teal-orange cinematic (exact hex values) |
| Basic text overlay | Character-pop animation on exact beat |
| Random hashtags | 4-tier hashtag strategy with trending data |
| Manual upload | Full YouTube API with OAuth |
| One-time setup | Persistent credentials (auto-refresh) |
| Single video only | Scalable batch processing |

---

**Built with:** Claude Code, FFmpeg, Google Veo 3.1, YouTube Data API v3  
**Author:** Muhammad Tayyab  
**Last Session:** 2026-04-16 — Tom Cruise Edit uploaded: `https://youtu.be/Lg5wp4X-QA8`
